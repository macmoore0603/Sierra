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

    func bringToFront() {
        NSApp.activate(ignoringOtherApps: true)
        for w in NSApp.windows where w.canBecomeMain {
            w.collectionBehavior.insert(.moveToActiveSpace)
            w.center()
            w.makeKeyAndOrderFront(nil)
            w.orderFrontRegardless()
        }
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

    let serverURL = "http://localhost:8000"
    private let wakeWords = ["hey sierra", "hey sira", "hello sierra", "ok sierra", "sierra"]
    private let vadThreshold: Float = 0.015
    private let clapThreshold: Float = 0.16

    private let socket = SierraSocketClient()

    private let audioEngine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private let synth = AVSpeechSynthesizer()

    private enum Mode: Equatable { case idle, capturing }
    private var mode: Mode = .idle
    private var silence: DispatchWorkItem?
    private var isSpeaking = false
    private var lastClap: Double = 0

    // MARK: Lifecycle
    func onAppear() {
        configureSocket()
        socket.connect()
        startListening()
    }

    func onDisappear() {
        socket.disconnect()
        teardownEngine()
        synth.stopSpeaking(at: .immediate)
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
    func startListening() {
        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            guard status == .authorized else { return }
            DispatchQueue.main.async { self?.startEngine() }
        }
    }

    private func startEngine() {
        guard !audioEngine.isRunning else { startRecognition(); return }
        let input = audioEngine.inputNode
        let format = input.outputFormat(forBus: 0)
        input.removeTap(onBus: 0)
        input.installTap(onBus: 0, bufferSize: 1024, format: format) { [weak self] buffer, _ in
            guard let self else { return }
            let level = self.rms(buffer)
            if level > self.vadThreshold { self.request?.append(buffer) }
            self.detectClap(level)
        }
        audioEngine.prepare()
        do { try audioEngine.start() } catch { print("Audio engine error: \(error)"); return }
        startRecognition()
    }

    private func startRecognition() {
        task?.cancel()
        let r = SFSpeechAudioBufferRecognitionRequest()
        r.shouldReportPartialResults = true
        if recognizer?.supportsOnDeviceRecognition == true { r.requiresOnDeviceRecognition = true }
        request = r
        task = recognizer?.recognitionTask(with: r) { [weak self] result, _ in
            guard let self, let result else { return }
            Task { @MainActor in self.handle(result.bestTranscription.formattedString) }
        }
    }

    private func restartRecognition() {
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
    private func speak(_ text: String) {
        guard !text.isEmpty else { return }
        isSpeaking = true
        let u = AVSpeechUtterance(string: text)
        u.voice = AVSpeechSynthesisVoice(language: "en-US")
        u.rate = 0.5
        synth.stopSpeaking(at: .immediate)
        synth.speak(u)
        // Mute the mic-guard for an estimate of the speech length, then clear
        // the buffer so we don't transcribe Sierra's own voice.
        let words = max(1, text.split(separator: " ").count)
        let estimate = max(1.2, Double(words) / 2.4 + 0.6)
        DispatchQueue.main.asyncAfter(deadline: .now() + estimate) { [weak self] in
            self?.isSpeaking = false
            self?.restartRecognition()
        }
    }

    // MARK: Clap-twice → bring the HUD to the front
    private func detectClap(_ level: Float) {
        guard level > clapThreshold else { return }
        let now = Date().timeIntervalSinceReferenceDate
        let dt = now - lastClap
        if dt > 0.12 && dt < 0.6 {                    // second clap of a pair
            lastClap = 0
            DispatchQueue.main.async { NotificationCenter.default.post(name: .sierraActivate, object: nil) }
        } else if dt > 0.12 {                         // first clap
            lastClap = now
        }
    }

    private func rms(_ buffer: AVAudioPCMBuffer) -> Float {
        guard let ch = buffer.floatChannelData?[0] else { return 0 }
        let n = Int(buffer.frameLength)
        var sum: Float = 0
        for i in 0..<n { sum += ch[i] * ch[i] }
        return sqrt(sum / Float(max(n, 1)))
    }

    private func teardownEngine() {
        silence?.cancel(); silence = nil
        if audioEngine.isRunning { audioEngine.stop() }
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
                let m = "Connection error. Is the backend running?"
                self.append(text: m, isUser: false, newBubble: true)
                self.speak(m)
            }
        }
    }

    private func sendToSierra(_ message: String) async throws -> String {
        let url = URL(string: "\(serverURL)/chat")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: ["message": message])
        let (data, _) = try await URLSession.shared.data(for: request)
        let result = try JSONDecoder().decode([String: String].self, from: data)
        return result["response"] ?? "No response"
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
                        infoRow("Voice", "On-device wake word + Gemini Live")
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
