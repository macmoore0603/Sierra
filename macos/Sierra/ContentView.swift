import SwiftUI
import Speech
import AVFoundation
import AppKit
import UserNotifications

extension Notification.Name {
    static let sierraActivate = Notification.Name("SierraActivate")
}

@main
struct SierraApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.hiddenTitleBar)
        .defaultSize(width: 1180, height: 760)
    }
}

class AppDelegate: NSObject, NSApplicationDelegate, UNUserNotificationCenterDelegate {
    var statusItem: NSStatusItem?

    func applicationDidFinishLaunching(_ notification: Notification) {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = statusItem?.button {
            button.image = NSImage(systemSymbolName: "sparkles", accessibilityDescription: "Sierra")
            button.action = #selector(toggleWindow)
            button.target = self
        }
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Open Sierra", action: #selector(toggleWindow), keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(NSApp.terminate(_:)), keyEquivalent: "q"))
        statusItem?.menu = menu

        UNUserNotificationCenter.current().delegate = self
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
            if granted {
                self.scheduleDailyBriefing()
            }
        }

        // Clap twice → bring the HUD to the front.
        NotificationCenter.default.addObserver(forName: .sierraActivate, object: nil, queue: .main) { [weak self] _ in
            self?.bringToFront()
        }

        // Make sure the HUD comes to the front on launch — on the user's CURRENT
        // Space — instead of opening behind other windows or on another desktop.
        NSApp.setActivationPolicy(.regular)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { self.bringToFront() }
    }

    /// Centre only the first time. Re-centring on every activation throws away
    /// wherever the user last dragged the window, which is felt every single
    /// time you clap or click the menu bar item.
    private var hasCentered = false

    func bringToFront() {
        NSApp.activate(ignoringOtherApps: true)
        for w in NSApp.windows where w.canBecomeMain {
            w.collectionBehavior.insert(.moveToActiveSpace)
            if !hasCentered { w.center() }
            w.makeKeyAndOrderFront(nil)
            w.orderFrontRegardless()
        }
        hasCentered = true
    }

    @objc func toggleWindow() {
        bringToFront()
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound])
    }

    func scheduleDailyBriefing() {
        let content = UNMutableNotificationContent()
        content.title = "Sierra Daily Briefing"
        content.body = "Good morning, Mac. Ready for today's update?"
        content.sound = .default

        var dateComponents = DateComponents()
        dateComponents.hour = 8
        dateComponents.minute = 0

        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
        let request = UNNotificationRequest(identifier: "daily-briefing", content: content, trigger: trigger)
        UNUserNotificationCenter.current().add(request)
    }
}

// MARK: - Audio-thread state
//
// `installTap` delivers buffers on a real-time audio thread. Everything the tap
// touches has to be safe to touch from there, so it lives here rather than on
// the main-actor view model — reaching back into that from the tap is a data
// race, and Swift 6's concurrency checking rejects it outright.
private final class AudioSink: @unchecked Sendable {
    private let lock = NSLock()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var lastClap: Double = 0
    private let clapThreshold: Float

    /// Called on the audio thread when a double-clap is detected.
    var onDoubleClap: (() -> Void)?

    init(clapThreshold: Float) { self.clapThreshold = clapThreshold }

    func use(_ request: SFSpeechAudioBufferRecognitionRequest?) {
        lock.lock(); defer { lock.unlock() }
        self.request = request
    }

    func receive(_ buffer: AVAudioPCMBuffer) {
        // Held across the append so the request cannot be swapped out from
        // under us mid-call. The critical section is microseconds.
        lock.lock()
        request?.append(buffer)
        lock.unlock()
        detectClap(Self.rms(buffer))
    }

    private func detectClap(_ level: Float) {
        guard level > clapThreshold else { return }
        let now = Date().timeIntervalSinceReferenceDate
        let dt = now - lastClap
        if dt > 0.12 && dt < 0.6 {          // second clap of a pair
            lastClap = 0
            onDoubleClap?()
        } else if dt > 0.12 {               // first clap
            lastClap = now
        }
    }

    private static func rms(_ buffer: AVAudioPCMBuffer) -> Float {
        guard let ch = buffer.floatChannelData?[0] else { return 0 }
        let n = Int(buffer.frameLength)
        guard n > 0 else { return 0 }
        var sum: Float = 0
        for i in 0..<n { sum += ch[i] * ch[i] }
        return sqrt(sum / Float(n))
    }
}

// Forwards synthesizer completion to the view model.
//
// `didCancel` matters as much as `didFinish`: `stopSpeaking(at:)` ends an
// utterance through the cancel path only, so listening for finish alone leaves
// the mic guard stuck on and the wake word dead for the rest of the session.
private final class SpeechEndObserver: NSObject, AVSpeechSynthesizerDelegate {
    var onEnd: ((AVSpeechUtterance) -> Void)?

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        onEnd?(utterance)
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        onEnd?(utterance)
    }
}

// MARK: - Backend errors

enum SierraBackendError: LocalizedError {
    case badURL(String)
    case http(status: Int, body: String)
    case malformed(String)

    var errorDescription: String? {
        switch self {
        case .badURL(let s):       return "Invalid backend address: \(s)"
        case .http(let code, _):   return "Backend returned HTTP \(code)"
        case .malformed:           return "Unexpected reply from the backend"
        }
    }
}

// MARK: - Real-time view model
//
// Owns the live connection to the Sierra backend. Voice turns run over the
// real-time Socket.IO pipeline (start_audio -> transcription / audio_data),
// while typed turns use the /chat REST endpoint. On-device speech recognition
// only listens for the "Hey Sierra" wake word, then hands the mic to the
// backend's Gemini Live session.
@MainActor
final class SierraViewModel: ObservableObject {
    @Published var messages: [Message] = []
    @Published var isListening = false          // a live backend session is active
    @Published var liveTranscription = ""       // on-device wake-word partials
    @Published var isConnected = false          // socket handshake complete
    @Published var serverStatus = "Connecting…"
    @Published var voiceStatus = "On-device wake word + Gemini Live"

    let serverURL = "http://localhost:8000"
    private let wakeWords = ["hey sierra", "hey sira", "hello sierra", "ok sierra", "sierra"]
    private let clapThreshold: Float = 0.16
    private let requestTimeout: TimeInterval = 30

    private let socket = SierraSocketClient()

    private let audioEngine = AVAudioEngine()
    private lazy var sink = AudioSink(clapThreshold: clapThreshold)
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private let synth = AVSpeechSynthesizer()
    private let speechObserver = SpeechEndObserver()

    private enum Mode: Equatable { case idle, capturing }
    private var mode: Mode = .idle
    private var silence: DispatchWorkItem?
    private var isSpeaking = false
    private var currentUtterance: AVSpeechUtterance?

    // MARK: Lifecycle
    func onAppear() {
        synth.delegate = speechObserver
        // Identity-matched: a late callback for an utterance we already replaced
        // must not clear the guard protecting the current one.
        speechObserver.onEnd = { [weak self] utterance in
            Task { @MainActor in
                guard let self, utterance === self.currentUtterance else { return }
                self.currentUtterance = nil
                self.isSpeaking = false
                self.restartRecognition()
            }
        }
        sink.onDoubleClap = {
            DispatchQueue.main.async {
                NotificationCenter.default.post(name: .sierraActivate, object: nil)
            }
        }
        configureSocket()
        socket.connect()
        startListening()
    }

    func onDisappear() {
        socket.disconnect()
        // Drop the guard first. Stopping the synthesizer fires the cancel
        // callback, and with the utterance still matched that would restart
        // recognition on an engine we are about to tear down.
        currentUtterance = nil
        isSpeaking = false
        synth.stopSpeaking(at: .immediate)
        teardownEngine()
    }

    private func configureSocket() {
        socket.onConnectedChange = { [weak self] connected in
            self?.isConnected = connected
            self?.serverStatus = connected ? "Online" : "Reconnecting…"
        }
        socket.onStatus = { [weak self] msg in self?.serverStatus = msg }
        socket.onError = { _ in }
        socket.onToolExecution = { [weak self] tool, realtime in
            let prefix = realtime ? "⚡️ Executing" : "⏳ Confirm"
            self?.append(text: "\(prefix) \(tool)…", isUser: false, newBubble: true)
        }
    }

    // MARK: Chat bubbles
    /// Append a message, or grow the last bubble in place when the same speaker
    /// keeps talking (so streaming partials update live instead of spamming).
    private func append(text: String, isUser: Bool, newBubble: Bool) {
        if !newBubble, let last = messages.last, last.isUser == isUser {
            messages[messages.count - 1].text = text
        } else {
            messages.append(Message(text: text, isUser: isUser))
        }
    }

    // MARK: Mic button (push-to-talk)
    func toggleVoice() {
        if mode == .capturing { finalizeCommand() } else { beginCapture(reset: true); armSilence() }
    }

    // MARK: On-device voice loop  (wake word → capture → /chat → speak)
    /// Speech recognition and the microphone are two separate grants. Asking only
    /// for speech leaves the engine tapping a mic the user never authorised, which
    /// yields silence at best.
    func startListening() {
        SFSpeechRecognizer.requestAuthorization { [weak self] speech in
            guard speech == .authorized else {
                Task { @MainActor in self?.voiceStatus = "Speech recognition access denied" }
                return
            }
            AVCaptureDevice.requestAccess(for: .audio) { micGranted in
                Task { @MainActor in
                    guard let self else { return }
                    guard micGranted else {
                        self.voiceStatus = "Microphone access denied"
                        return
                    }
                    self.startEngine()
                }
            }
        }
    }

    private func startEngine() {
        guard !audioEngine.isRunning else { startRecognition(); return }
        let input = audioEngine.inputNode
        let format = input.outputFormat(forBus: 0)
        // installTap raises an exception on a zero-channel / zero-rate format,
        // which is what an unavailable input device reports. Refuse instead.
        guard format.channelCount > 0, format.sampleRate > 0 else {
            voiceStatus = "No usable audio input device"
            return
        }
        input.removeTap(onBus: 0)
        input.installTap(onBus: 0, bufferSize: 1024, format: format) { [sink] buffer, _ in
            sink.receive(buffer)
        }
        audioEngine.prepare()
        do {
            try audioEngine.start()
        } catch {
            voiceStatus = "Audio engine failed: \(error.localizedDescription)"
            return
        }
        voiceStatus = "On-device wake word + Gemini Live"
        startRecognition()
    }

    private func startRecognition() {
        task?.cancel()
        let r = SFSpeechAudioBufferRecognitionRequest()
        r.shouldReportPartialResults = true
        if recognizer?.supportsOnDeviceRecognition == true { r.requiresOnDeviceRecognition = true }
        request = r
        sink.use(r)
        task = recognizer?.recognitionTask(with: r) { [weak self] result, _ in
            guard let self, let result else { return }
            Task { @MainActor in self.handle(result.bestTranscription.formattedString) }
        }
    }

    private func restartRecognition() {
        sink.use(nil)
        request?.endAudio()
        startRecognition()
    }

    private func handle(_ transcript: String) {
        guard !isSpeaking else { return }            // ignore Sierra's own voice
        let lower = transcript.lowercased()
        if let r = wakeRange(in: lower) {
            let after = String(lower[r.upperBound...]).trimmingCharacters(in: .whitespacesAndNewlines)
            if mode == .idle { beginCapture(reset: false) }
            liveTranscription = after
            armSilence()
        } else if mode == .capturing {
            liveTranscription = lower.trimmingCharacters(in: .whitespacesAndNewlines)
            armSilence()
        }
    }

    private func wakeRange(in lower: String) -> Range<String.Index>? {
        for w in wakeWords { if let r = lower.range(of: w) { return r } }
        return nil
    }

    private func beginCapture(reset: Bool) {
        mode = .capturing
        isListening = true
        if reset { liveTranscription = "" }
    }

    private func armSilence() {
        silence?.cancel()
        let work = DispatchWorkItem { [weak self] in self?.finalizeCommand() }
        silence = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.3, execute: work)
    }

    private func finalizeCommand() {
        silence?.cancel(); silence = nil
        let cmd = liveTranscription.trimmingCharacters(in: .whitespacesAndNewlines)
        mode = .idle
        isListening = false
        liveTranscription = ""
        restartRecognition()                         // clear the buffer for the next turn
        if !cmd.isEmpty { send(cmd) }
    }

    // MARK: Speak the reply (system voice — instant, no API, no quota)
    /// The mic guard is lifted by the synthesizer's own completion callback, not
    /// by a word-count estimate. Guessing cuts both ways: guess short and Sierra
    /// transcribes its own voice — the exact thing the guard exists to stop —
    /// guess long and it goes deaf to the user for the remainder.
    private func speak(_ text: String) {
        guard !text.isEmpty else { return }
        let u = AVSpeechUtterance(string: text)
        u.voice = AVSpeechSynthesisVoice(language: "en-US")
        u.rate = 0.5
        synth.stopSpeaking(at: .immediate)
        // Set after stopping: the cancel callback for the previous utterance is
        // identity-matched, so it cannot clear the guard we are about to raise.
        currentUtterance = u
        isSpeaking = true
        synth.speak(u)
    }

    private func teardownEngine() {
        silence?.cancel(); silence = nil
        if audioEngine.isRunning { audioEngine.stop() }
        sink.use(nil)
        request?.endAudio(); task?.cancel(); request = nil; task = nil
        audioEngine.inputNode.removeTap(onBus: 0)
    }

    // MARK: Send to /chat (typed or spoken) — reply is shown and spoken
    func send(_ text: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        append(text: trimmed, isUser: true, newBubble: true)
        Task {
            do {
                let response = try await sendToSierra(trimmed)
                self.append(text: response, isUser: false, newBubble: true)
                self.speak(response)
            } catch {
                // Say which of the three it was. "Is the backend running?" sent
                // you to check a process that answered fine and returned a 500.
                let m: String
                switch error {
                case let e as SierraBackendError:
                    m = e.errorDescription ?? "Backend error"
                case let e as URLError where e.code == .timedOut:
                    m = "Sierra did not reply within \(Int(requestTimeout))s."
                default:
                    m = "Can't reach Sierra at \(serverURL). Is the backend running?"
                }
                self.append(text: m, isUser: false, newBubble: true)
                self.speak(m)
            }
        }
    }

    /// Decoded leniently on purpose. The previous `[String: String]` decode threw
    /// on any reply carrying a non-string value — a `tool_calls` array, an `ok`
    /// flag — and the throw surfaced as "is the backend running?" for a backend
    /// that had just answered correctly.
    private struct ChatReply: Decodable {
        let response: String?
        let error: String?
    }

    private func sendToSierra(_ message: String) async throws -> String {
        guard let url = URL(string: "\(serverURL)/chat") else {
            throw SierraBackendError.badURL(serverURL)
        }
        var request = URLRequest(url: url, timeoutInterval: requestTimeout)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: ["message": message])

        let (data, response) = try await URLSession.shared.data(for: request)
        if let http = response as? HTTPURLResponse, !(200..<300).contains(http.statusCode) {
            let body = String(data: data, encoding: .utf8) ?? ""
            throw SierraBackendError.http(status: http.statusCode, body: body)
        }

        guard let reply = try? JSONDecoder().decode(ChatReply.self, from: data) else {
            throw SierraBackendError.malformed(String(data: data, encoding: .utf8) ?? "")
        }
        if let e = reply.error, !e.isEmpty { throw SierraBackendError.malformed(e) }
        guard let text = reply.response, !text.isEmpty else {
            throw SierraBackendError.malformed("reply contained no 'response' field")
        }
        return text
    }
}

// MARK: - Tabs

enum SierraTab: String, CaseIterable, Identifiable {
    case chat = "Chat"
    case tools = "Tools"
    case devices = "Devices"
    case settings = "Settings"
    var id: String { rawValue }
    var icon: String {
        switch self {
        case .chat: return "waveform"
        case .tools: return "wrench.and.screwdriver.fill"
        case .devices: return "house.fill"
        case .settings: return "gearshape.fill"
        }
    }
}

// MARK: - Root

struct ContentView: View {
    @StateObject private var vm = SierraViewModel()
    @State private var inputText = ""
    @State private var tab: SierraTab = .chat

    var body: some View {
        ZStack {
            Theme.backdrop.ignoresSafeArea()
            VStack(spacing: 0) {
                header
                hudBar
                tabBar
                Rectangle().fill(Theme.gold.opacity(0.18)).frame(height: 1)
                content
            }
        }
        .preferredColorScheme(.dark)
        .frame(minWidth: 940, minHeight: 680)
        .onAppear { vm.onAppear() }
        .onDisappear { vm.onDisappear() }
    }

    private var header: some View {
        HStack(spacing: 14) {
            Text("SIERRA")
                .font(.system(size: 30, weight: .heavy, design: .rounded))
                .foregroundStyle(Theme.metalGold)
                .shadow(color: Theme.gold.opacity(0.5), radius: 8)
            Text("JARVIS-CLASS ASSISTANT")
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .tracking(2)
                .foregroundColor(Theme.textDim)
            Spacer()
            ConnectionPill(connected: vm.isConnected, status: vm.serverStatus)
        }
        .padding(.horizontal, 26)
        .padding(.vertical, 16)
        .background(Theme.bg0.opacity(0.55))
    }

    private var hudBar: some View {
        HStack(spacing: 16) {
            StatusPills(connected: vm.isConnected, listening: vm.isListening)
            Spacer(minLength: 12)
            TopAudioBar(active: vm.isListening)
                .frame(width: 240)
                .opacity(0.9)
        }
        .padding(.horizontal, 24)
        .padding(.bottom, 12)
    }

    private var tabBar: some View {
        HStack(spacing: 6) {
            ForEach(SierraTab.allCases) { t in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) { tab = t }
                } label: {
                    HStack(spacing: 8) {
                        Image(systemName: t.icon)
                        Text(t.rawValue).font(.system(size: 13, weight: .semibold, design: .rounded))
                    }
                    .foregroundStyle(tab == t ? AnyShapeStyle(Theme.metalGold) : AnyShapeStyle(Theme.textDim))
                    .padding(.horizontal, 16)
                    .padding(.vertical, 9)
                    .background(
                        RoundedRectangle(cornerRadius: 11, style: .continuous)
                            .fill(tab == t ? Theme.gold.opacity(0.12) : .clear)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 11, style: .continuous)
                            .strokeBorder(tab == t ? Theme.gold.opacity(0.5) : .clear, lineWidth: 1)
                    )
                }
                .buttonStyle(.plain)
            }
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.bottom, 12)
    }

    @ViewBuilder private var content: some View {
        switch tab {
        case .chat:
            JarvisHUD(vm: vm, inputText: $inputText)
        case .tools:
            ToolsTab { starter in
                inputText = starter
                withAnimation(.easeInOut(duration: 0.2)) { tab = .chat }
            }
        case .devices:
            DevicesTab(vm: vm)
        case .settings:
            SettingsTab(vm: vm)
        }
    }
}

// MARK: - Connection pill

struct ConnectionPill: View {
    let connected: Bool
    let status: String
    var body: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(connected ? Color.green : Color(hex: 0xC0392B))
                .frame(width: 9, height: 9)
                .shadow(color: connected ? .green : .red, radius: 5)
            Text(status)
                .font(.system(size: 11, weight: .medium, design: .monospaced))
                .foregroundColor(Theme.textDim)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 7)
        .background(Capsule().fill(Theme.panel.opacity(0.8)))
        .overlay(Capsule().strokeBorder(Theme.gold.opacity(0.3), lineWidth: 1))
    }
}

// MARK: - Chat tab

struct ChatTab: View {
    @ObservedObject var vm: SierraViewModel
    @Binding var inputText: String
    @FocusState private var inputFocused: Bool

    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            reactorPanel
                .frame(width: 252)
            chatPanel
        }
        .padding(20)
        .onAppear { if !inputText.isEmpty { inputFocused = true } }
    }

    private var reactorPanel: some View {
        VStack(spacing: 14) {
            ArcReactorView(isListening: vm.isListening, size: 210)
                .padding(.top, 6)
            Text(vm.isListening ? "LISTENING" : (vm.isConnected ? "READY" : "OFFLINE"))
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .tracking(3)
                .foregroundStyle(Theme.metalGold)
            if !vm.liveTranscription.isEmpty {
                Text("🎙️ \(vm.liveTranscription)")
                    .font(.caption)
                    .foregroundColor(Theme.gold)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
            }
            Spacer()
            micButton
        }
        .frame(maxHeight: .infinity)
    }

    private var micButton: some View {
        Button(action: vm.toggleVoice) {
            ZStack {
                Circle()
                    .fill(vm.isListening ? AnyShapeStyle(Color(hex: 0xC0392B)) : AnyShapeStyle(Theme.metalGold))
                    .frame(width: 64, height: 64)
                    .shadow(color: (vm.isListening ? Color.red : Theme.gold).opacity(0.7), radius: 16)
                Image(systemName: vm.isListening ? "stop.fill" : "mic.fill")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.black)
            }
        }
        .buttonStyle(.plain)
        .help(vm.isListening ? "Stop listening" : "Talk to Sierra")
    }

    private var chatPanel: some View {
        VStack(spacing: 12) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 14) {
                        if vm.messages.isEmpty {
                            VStack(spacing: 8) {
                                Image(systemName: "sparkles").font(.title).foregroundStyle(Theme.metalGold)
                                Text("Say “Hey Sierra” or type below.")
                                    .font(.callout).foregroundColor(Theme.textDim)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.top, 60)
                        }
                        ForEach(vm.messages) { msg in
                            ChatBubble(text: msg.text, isUser: msg.isUser).id(msg.id)
                        }
                    }
                    .padding(16)
                }
                .onChange(of: vm.messages.last?.id) { _, _ in scrollToEnd(proxy) }
                .onChange(of: vm.messages.last?.text) { _, _ in scrollToEnd(proxy) }
            }
            .background(
                RoundedRectangle(cornerRadius: 18, style: .continuous).fill(Theme.bg1.opacity(0.5))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .strokeBorder(Theme.gold.opacity(0.18), lineWidth: 1)
            )
            inputBar
        }
    }

    private var inputBar: some View {
        HStack(spacing: 12) {
            TextField("Speak or type to Sierra…", text: $inputText)
                .textFieldStyle(.plain)
                .focused($inputFocused)
                .foregroundColor(Theme.textPrimary)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(Capsule().fill(Theme.panel.opacity(0.9)))
                .overlay(Capsule().strokeBorder(Theme.goldStroke, lineWidth: 1.4))
                .onSubmit(send)
            Button(action: send) {
                Image(systemName: "paperplane.fill")
                    .font(.title3)
                    .foregroundStyle(Theme.metalGold)
            }
            .buttonStyle(.plain)
        }
    }

    private func send() {
        let text = inputText
        inputText = ""
        vm.send(text)
    }

    private func scrollToEnd(_ proxy: ScrollViewProxy) {
        guard let id = vm.messages.last?.id else { return }
        withAnimation(.easeOut(duration: 0.25)) { proxy.scrollTo(id, anchor: .bottom) }
    }
}

struct ChatBubble: View {
    let text: String
    let isUser: Bool
    var body: some View {
        HStack {
            if isUser { Spacer(minLength: 48) }
            Text(text)
                .font(.system(size: 14))
                .foregroundColor(isUser ? .black : Theme.textPrimary)
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background {
                    if isUser {
                        RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Theme.metalGold)
                    } else {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(Theme.panel)
                            .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .strokeBorder(Theme.gold.opacity(0.25), lineWidth: 1))
                    }
                }
                .shadow(color: isUser ? Theme.gold.opacity(0.3) : .clear, radius: 8)
            if !isUser { Spacer(minLength: 48) }
        }
    }
}

// MARK: - Tools tab

struct ToolsTab: View {
    var onPick: (String) -> Void

    private struct Tool: Identifiable {
        let id = UUID()
        let icon: String, title: String, desc: String, starter: String
    }
    private let tools: [Tool] = [
        .init(icon: "cube.transparent", title: "CAD & 3D", desc: "Design printable 3D models", starter: "Generate a CAD model of "),
        .init(icon: "globe", title: "Web", desc: "Browse & research online", starter: "Search the web for "),
        .init(icon: "folder", title: "Files", desc: "Read & write project files", starter: "Read the file "),
        .init(icon: "lightbulb.led", title: "Smart Home", desc: "Control your lights & plugs", starter: "Turn on the "),
        .init(icon: "printer", title: "3D Printer", desc: "Send prints & check status", starter: "Check my printer status"),
        .init(icon: "square.stack.3d.up", title: "Projects", desc: "Organize work into projects", starter: "Create a new project called "),
        .init(icon: "eye", title: "Vision", desc: "See through your camera", starter: "What do you see?"),
        .init(icon: "sun.max", title: "Briefing", desc: "Your daily summary", starter: "Give me my daily briefing"),
    ]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 220), spacing: 14)], spacing: 14) {
                ForEach(tools) { t in
                    Button { onPick(t.starter) } label: {
                        GoldPanel {
                            HStack(spacing: 14) {
                                Image(systemName: t.icon)
                                    .font(.system(size: 22, weight: .semibold))
                                    .foregroundStyle(Theme.metalGold)
                                    .frame(width: 34)
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(t.title).font(.system(size: 15, weight: .bold))
                                        .foregroundColor(Theme.textPrimary)
                                    Text(t.desc).font(.caption).foregroundColor(Theme.textDim)
                                }
                                Spacer()
                            }
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(20)
        }
    }
}

// MARK: - Devices tab

struct DevicesTab: View {
    @ObservedObject var vm: SierraViewModel
    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                GoldPanel {
                    HStack(spacing: 12) {
                        Image(systemName: vm.isConnected ? "bolt.fill" : "bolt.slash.fill")
                            .foregroundStyle(Theme.metalGold).font(.title3)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Backend").font(.headline).foregroundColor(Theme.textPrimary)
                            Text(vm.isConnected ? "Connected — \(vm.serverStatus)" : vm.serverStatus)
                                .font(.caption).foregroundColor(Theme.textDim)
                        }
                        Spacer()
                    }
                }
                deviceRow(icon: "lightbulb.led", title: "Smart Home (Kasa)",
                          hint: "Ask Sierra to “list my smart devices” or “turn on the lamp”.")
                deviceRow(icon: "printer", title: "3D Printers",
                          hint: "Ask “discover printers” or “check my printer status”.")
                deviceRow(icon: "camera", title: "Camera & Presence",
                          hint: "Vision and gesture features run through the backend.")
                Spacer()
            }
            .padding(20)
        }
    }

    private func deviceRow(icon: String, title: String, hint: String) -> some View {
        GoldPanel {
            HStack(spacing: 12) {
                Image(systemName: icon).foregroundStyle(Theme.metalGold).font(.title3).frame(width: 30)
                VStack(alignment: .leading, spacing: 2) {
                    Text(title).font(.headline).foregroundColor(Theme.textPrimary)
                    Text(hint).font(.caption).foregroundColor(Theme.textDim)
                }
                Spacer()
            }
        }
    }
}

// MARK: - Settings tab

struct SettingsTab: View {
    @ObservedObject var vm: SierraViewModel
    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                GoldPanel {
                    VStack(alignment: .leading, spacing: 12) {
                        infoRow("Backend", vm.serverURL)
                        Divider().overlay(Theme.gold.opacity(0.15))
                        infoRow("Status", vm.serverStatus)
                        Divider().overlay(Theme.gold.opacity(0.15))
                        infoRow("Wake words", "Hey Sierra · Sierra · OK Sierra")
                        Divider().overlay(Theme.gold.opacity(0.15))
                        infoRow("Real-time execution", "God Mode — on")
                        Divider().overlay(Theme.gold.opacity(0.15))
                        infoRow("Voice", vm.voiceStatus)
                        Divider().overlay(Theme.gold.opacity(0.15))
                        infoRow("Version", "Sierra 1.0 · metallic-gold")
                    }
                }
                HStack(spacing: 12) {
                    actionButton(vm.isListening ? "Stop Listening" : "Start Listening",
                                 icon: vm.isListening ? "stop.fill" : "mic.fill") { vm.toggleVoice() }
                    actionButton("Say Hello", icon: "hand.wave.fill") { vm.send("Hello Sierra, introduce yourself in one sentence.") }
                }
                Spacer()
            }
            .padding(20)
        }
    }

    private func infoRow(_ label: String, _ value: String) -> some View {
        HStack {
            Text(label).font(.system(size: 13, weight: .semibold)).foregroundColor(Theme.textDim)
            Spacer()
            Text(value).font(.system(size: 13, design: .monospaced)).foregroundColor(Theme.textPrimary)
        }
    }

    private func actionButton(_ title: String, icon: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                Text(title).font(.system(size: 13, weight: .semibold))
            }
            .foregroundColor(.black)
            .padding(.horizontal, 18).padding(.vertical, 11)
            .background(Capsule().fill(Theme.metalGold))
            .shadow(color: Theme.gold.opacity(0.4), radius: 8)
        }
        .buttonStyle(.plain)
    }
}

struct Message: Identifiable {
    let id = UUID()
    var text: String
    let isUser: Bool
}
