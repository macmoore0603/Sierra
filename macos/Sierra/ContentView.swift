import SwiftUI
import Speech
import AVFoundation
import AppKit
import UserNotifications

@main
struct SierraApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.hiddenTitleBar)
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
    }

    @objc func toggleWindow() {
        NSApp.activate(ignoringOtherApps: true)
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
    private let customWakeWords = ["hey sierra", "sierra", "hey sira", "hello sierra", "ok sierra"]
    private let vadThreshold: Float = 0.017

    private let socket = SierraSocketClient()
    private let audioPlayer = AudioStreamPlayer()

    private let audioEngine = AVAudioEngine()
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))

    // MARK: Lifecycle
    func onAppear() {
        configureSocket()
        socket.connect()
        startWakeWordDetection()
    }

    func onDisappear() {
        if isListening { stopSession() }
        socket.disconnect()
        stopAudioEngine()
    }

    private func configureSocket() {
        socket.onConnectedChange = { [weak self] connected in
            self?.isConnected = connected
            self?.serverStatus = connected ? "Online" : "Reconnecting…"
        }
        socket.onStatus = { [weak self] msg in self?.serverStatus = msg }
        socket.onError = { [weak self] msg in
            self?.append(text: "⚠️ \(msg)", isUser: false, newBubble: true)
        }
        socket.onTranscription = { [weak self] sender, text in
            self?.liveTranscription = ""
            self?.append(text: text, isUser: sender.lowercased() == "user", newBubble: false)
        }
        socket.onAudio = { [weak self] data in
            self?.audioPlayer.enqueue(data)
        }
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

    // MARK: Voice session (real-time)
    func toggleVoice() {
        isListening ? stopSession() : startSession()
    }

    private func startSession() {
        guard !isListening else { return }
        stopAudioEngine()                 // free the mic for the backend's session
        audioPlayer.start()
        socket.startAudio()
        isListening = true
        liveTranscription = ""
    }

    private func stopSession() {
        guard isListening else { return }
        socket.stopAudio()
        audioPlayer.stop()
        isListening = false
        liveTranscription = ""
        startWakeWordDetection()          // resume listening for the wake word
    }

    // MARK: On-device wake word
    func startWakeWordDetection() {
        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            guard status == .authorized else { return }
            DispatchQueue.main.async { self?.beginWakeWordEngine() }
        }
    }

    private func beginWakeWordEngine() {
        guard !isListening else { return }
        do {
            let inputNode = audioEngine.inputNode
            let recordingFormat = inputNode.outputFormat(forBus: 0)
            inputNode.removeTap(onBus: 0)

            let request = SFSpeechAudioBufferRecognitionRequest()
            request.shouldReportPartialResults = true
            recognitionRequest = request

            inputNode.installTap(onBus: 0, bufferSize: 512, format: recordingFormat) { [weak self] buffer, _ in
                guard let self else { return }
                if self.calculateRMS(buffer: buffer) > self.vadThreshold {
                    self.recognitionRequest?.append(buffer)
                }
            }

            audioEngine.prepare()
            try audioEngine.start()

            recognitionTask = speechRecognizer?.recognitionTask(with: request) { [weak self] result, _ in
                guard let self, let result else { return }
                Task { @MainActor in
                    guard !self.isListening else { return }
                    let transcript = result.bestTranscription.formattedString
                    self.liveTranscription = transcript
                    let text = transcript.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
                    if self.customWakeWords.contains(where: { text.contains($0) }) {
                        self.handleWakeWordDetected()
                    }
                }
            }
        } catch {
            print("Wake word error: \(error)")
        }
    }

    private func handleWakeWordDetected() {
        append(text: "Hey Sierra", isUser: true, newBubble: true)
        startSession()                    // hand off to the real-time backend session
    }

    private func calculateRMS(buffer: AVAudioPCMBuffer) -> Float {
        guard let channelData = buffer.floatChannelData?[0] else { return 0.0 }
        let frameLength = Int(buffer.frameLength)
        var sum: Float = 0.0
        for i in 0..<frameLength { sum += channelData[i] * channelData[i] }
        return sqrt(sum / Float(max(frameLength, 1)))
    }

    private func stopAudioEngine() {
        if audioEngine.isRunning { audioEngine.stop() }
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        recognitionRequest = nil
        recognitionTask = nil
        audioEngine.inputNode.removeTap(onBus: 0)
    }

    // MARK: Typed text (REST /chat)
    func send(_ text: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        append(text: trimmed, isUser: true, newBubble: true)
        Task {
            do {
                let response = try await sendToSierra(trimmed)
                self.append(text: response, isUser: false, newBubble: true)
            } catch {
                self.append(text: "Connection error. Is the backend running?", isUser: false, newBubble: true)
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

struct ContentView: View {
    @StateObject private var vm = SierraViewModel()
    @State private var inputText = ""
    @State private var reactorScale: CGFloat = 1.0
    @State private var reactorGlow: Double = 0.8
    @State private var reactorRotation: Double = 0.0

    var body: some View {
        ZStack {
            LinearGradient(gradient: Gradient(colors: [Color.black, Color(red: 0.12, green: 0.08, blue: 0.0), Color.black]), startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()

            VStack(spacing: 0) {
                HStack {
                    Text("SIERRA")
                        .font(.system(size: 38, weight: .bold, design: .rounded))
                        .foregroundStyle(LinearGradient(colors: [.yellow, .orange, .yellow], startPoint: .leading, endPoint: .trailing))
                    Circle()
                        .fill(vm.isConnected ? Color.green : Color.red)
                        .frame(width: 10, height: 10)
                        .shadow(color: vm.isConnected ? .green : .red, radius: 6)
                    Text(vm.serverStatus)
                        .font(.caption2)
                        .foregroundColor(.gray)
                    Spacer()
                    Text("LEXUS NEXUS CAPITAL")
                        .font(.caption.bold())
                        .foregroundColor(.yellow.opacity(0.9))
                }
                .padding(.horizontal, 28)
                .padding(.vertical, 14)
                .background(.black.opacity(0.9))

                ZStack {
                    Circle().stroke(Color.yellow.opacity(0.25), lineWidth: 10)
                        .frame(width: 220, height: 220)
                        .rotationEffect(.degrees(reactorRotation))

                    Circle()
                        .stroke(LinearGradient(colors: [.yellow, .orange, .yellow], startPoint: .top, endPoint: .bottom), lineWidth: 18)
                        .frame(width: 180, height: 180)
                        .scaleEffect(reactorScale)
                        .opacity(reactorGlow)

                    Circle()
                        .fill(RadialGradient(colors: [.yellow, .orange, .black], center: .center, startRadius: 25, endRadius: 70))
                        .frame(width: 110, height: 110)
                        .shadow(color: .yellow, radius: 40)
                }
                .padding(.top, 30)
                .onChange(of: vm.isListening) { _, newValue in
                    withAnimation(.easeInOut(duration: 0.3).repeatForever(autoreverses: true)) {
                        reactorScale = newValue ? 1.32 : 1.0
                        reactorGlow = newValue ? 1.0 : 0.7
                    }
                    withAnimation(.linear(duration: 1.4).repeatForever(autoreverses: false)) {
                        reactorRotation = newValue ? 360 : 0
                    }
                }

                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 20) {
                            ForEach(vm.messages) { msg in
                                ChatBubble(text: msg.text, isUser: msg.isUser)
                                    .id(msg.id)
                            }
                        }
                        .padding(24)
                    }
                    // Keep the newest message in view as turns stream in.
                    .onChange(of: vm.messages.last?.id) { _, _ in
                        if let lastID = vm.messages.last?.id {
                            withAnimation(.easeOut(duration: 0.25)) {
                                proxy.scrollTo(lastID, anchor: .bottom)
                            }
                        }
                    }
                    .onChange(of: vm.messages.last?.text) { _, _ in
                        if let lastID = vm.messages.last?.id {
                            proxy.scrollTo(lastID, anchor: .bottom)
                        }
                    }
                }

                if !vm.liveTranscription.isEmpty {
                    Text("🎙️ \(vm.liveTranscription)")
                        .font(.caption)
                        .foregroundColor(.yellow)
                        .padding(10)
                        .background(Color.yellow.opacity(0.2))
                        .cornerRadius(16)
                        .padding(.horizontal)
                }

                HStack(spacing: 16) {
                    TextField("Speak or type to Sierra...", text: $inputText)
                        .textFieldStyle(.plain)
                        .padding(16)
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(30)
                        .overlay(RoundedRectangle(cornerRadius: 30).strokeBorder(LinearGradient(colors: [.yellow.opacity(0.7), .orange.opacity(0.5)], startPoint: .leading, endPoint: .trailing), lineWidth: 1.5))
                        .onSubmit(sendTyped)

                    Button(action: sendTyped) {
                        Image(systemName: "paperplane.fill")
                            .font(.title2)
                            .foregroundColor(.yellow)
                    }
                    .buttonStyle(.plain)

                    Button(action: vm.toggleVoice) {
                        Image(systemName: vm.isListening ? "waveform.path" : "mic.circle.fill")
                            .font(.largeTitle)
                            .foregroundStyle(vm.isListening ? .red : .yellow)
                            .symbolEffect(.pulse, isActive: vm.isListening)
                    }
                    .buttonStyle(.plain)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 32)
            }
        }
        .preferredColorScheme(.dark)
        .onAppear { vm.onAppear() }
        .onDisappear { vm.onDisappear() }
    }

    private func sendTyped() {
        let text = inputText
        inputText = ""
        vm.send(text)
    }
}

struct ChatBubble: View {
    let text: String
    let isUser: Bool
    var body: some View {
        HStack {
            if isUser { Spacer() }
            Text(text)
                .padding(16)
                .background(isUser ? AnyShapeStyle(LinearGradient(colors: [.yellow, .orange], startPoint: .topLeading, endPoint: .bottomTrailing)) : AnyShapeStyle(Color.white.opacity(0.08)))
                .foregroundColor(isUser ? .black : .white)
                .cornerRadius(22)
                .shadow(color: isUser ? .yellow.opacity(0.5) : .clear, radius: 10)
            if !isUser { Spacer() }
        }
    }
}

struct Message: Identifiable {
    let id = UUID()
    var text: String
    let isUser: Bool
}
