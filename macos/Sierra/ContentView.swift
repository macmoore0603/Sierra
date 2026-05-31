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

struct ContentView: View {
    @State private var messages: [Message] = []
    @State private var inputText = ""
    @State private var isListening = false
    @State private var isLoading = false
    @State private var liveTranscription = ""
    @State private var reactorScale: CGFloat = 1.0
    @State private var reactorGlow: Double = 0.8
    @State private var reactorRotation: Double = 0.0
    
    @State private var audioEngine = AVAudioEngine()
    @State private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    @State private var recognitionTask: SFSpeechRecognitionTask?
    @State private var speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    
    let serverURL = "http://localhost:8000"
    @State private var customWakeWords: [String] = ["hey sierra", "sierra", "hey sira", "hello sierra", "ok sierra"]
    let vadThreshold: Float = 0.017
    
    var body: some View {
        ZStack {
            LinearGradient(gradient: Gradient(colors: [Color.black, Color(red: 0.12, green: 0.08, blue: 0.0), Color.black]), startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                HStack {
                    Text("SIERRA")
                        .font(.system(size: 38, weight: .bold, design: .rounded))
                        .foregroundStyle(LinearGradient(colors: [.yellow, .orange, .yellow], startPoint: .leading, endPoint: .trailing))
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
                // FIXED: Updated syntax for modern Xcode versions
                .onChange(of: isListening) { oldValue, newValue in
                    withAnimation(.easeInOut(duration: 0.3).repeatForever(autoreverses: true)) {
                        reactorScale = newValue ? 1.32 : 1.0
                        reactorGlow = newValue ? 1.0 : 0.7
                    }
                    withAnimation(.linear(duration: 1.4).repeatForever(autoreverses: false)) {
                        reactorRotation = newValue ? 360 : 0
                    }
                }
                
                ScrollView {
                    LazyVStack(spacing: 20) {
                        ForEach(messages) { msg in
                            ChatBubble(text: msg.text, isUser: msg.isUser)
                        }
                    }
                    .padding(24)
                }
                
                if !liveTranscription.isEmpty {
                    Text("🎙️ \(liveTranscription)")
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
                    
                    Button(action: sendMessage) {
                        Image(systemName: "paperplane.fill")
                            .font(.title2)
                            .foregroundColor(.yellow)
                    }
                    .buttonStyle(.plain) // FIXED: Removes default macOS button framing
                    
                    Button(action: toggleVoice) {
                        Image(systemName: isListening ? "waveform.path" : "mic.circle.fill")
                            .font(.largeTitle)
                            .foregroundStyle(isListening ? .red : .yellow)
                            .symbolEffect(.pulse, isActive: isListening)
                    }
                    .buttonStyle(.plain) // FIXED: Removes default macOS button framing
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 32)
            }
        }
        .preferredColorScheme(.dark)
        .onAppear {
            startWakeWordDetection()
        }
        .onDisappear { stopAudioEngine() }
    }
    
    func startWakeWordDetection() {
        SFSpeechRecognizer.requestAuthorization { status in
            guard status == .authorized else { return }
            do {
                let inputNode = self.audioEngine.inputNode
                let recordingFormat = inputNode.outputFormat(forBus: 0)
                
                inputNode.removeTap(onBus: 0)
                
                inputNode.installTap(onBus: 0, bufferSize: 512, format: recordingFormat) { buffer, _ in
                    let rms = self.calculateRMS(buffer: buffer)
                    if rms > self.vadThreshold {
                        self.recognitionRequest?.append(buffer)
                    }
                }
                
                self.recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
                self.recognitionRequest?.shouldReportPartialResults = true
                
                self.audioEngine.prepare()
                try self.audioEngine.start()
                
                self.recognitionTask = self.speechRecognizer?.recognitionTask(with: self.recognitionRequest!) { result, error in
                    guard let result = result else { return }
                    
                    // FIXED: UI updates must happen explicitly on the MainActor/Main Thread
                    Task { @MainActor in
                        self.liveTranscription = result.bestTranscription.formattedString
                        
                        let text = result.bestTranscription.formattedString.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
                        
                        if self.customWakeWords.contains(where: { text.contains($0) }) && !self.isListening {
                            self.handleWakeWordDetected()
                        }
                    }
                }
            } catch {
                print("Wake word error: \(error)")
            }
        }
    }
    
    func handleWakeWordDetected() {
        isListening = true
        messages.append(Message(text: "Hey Sierra", isUser: true))
        liveTranscription = ""
        
        Task {
            do {
                let response = try await sendToSierra("Hello Sierra. Be proactive.")
                // FIXED: Wrapped in MainActor task to avoid background state alteration
                await MainActor.run {
                    messages.append(Message(text: response, isUser: false))
                }
            } catch {}
            
            try? await Task.sleep(nanoseconds: 3_000_000_000)
            await MainActor.run {
                self.isListening = false
                self.liveTranscription = ""
            }
        }
    }
    
    func calculateRMS(buffer: AVAudioPCMBuffer) -> Float {
        guard let channelData = buffer.floatChannelData?[0] else { return 0.0 }
        let frameLength = Int(buffer.frameLength)
        var sum: Float = 0.0
        for i in 0..<frameLength {
            sum += channelData[i] * channelData[i]
        }
        return sqrt(sum / Float(frameLength))
    }
    
    func stopAudioEngine() {
        audioEngine.stop()
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        audioEngine.inputNode.removeTap(onBus: 0)
        liveTranscription = ""
    }
    
    func toggleVoice() { isListening.toggle() }
    
    func sendMessage() {
        guard !inputText.isEmpty else { return }
        let text = inputText
        messages.append(Message(text: text, isUser: true))
        inputText = ""
        isLoading = true
        
        Task {
            do {
                let response = try await sendToSierra(text)
                await MainActor.run {
                    withAnimation { messages.append(Message(text: response, isUser: false)) }
                }
            } catch {
                await MainActor.run {
                    messages.append(Message(text: "Connection error. Is backend running?", isUser: false))
                }
            }
            await MainActor.run {
                isLoading = false
            }
        }
    }
    
    func sendToSierra(_ message: String) async throws -> String {
        let url = URL(string: "\(serverURL)/chat")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["message": message]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let result = try JSONDecoder().decode([String: String].self, from: data)
        return result["response"] ?? "No response"
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
    let text: String
    let isUser: Bool
}
