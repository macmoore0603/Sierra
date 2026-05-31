//
//  SierraSocketClient.swift
//  Sierra
//
//  A minimal, dependency-free Socket.IO (v5) / Engine.IO (v4) client built on
//  URLSessionWebSocketTask. It speaks just enough of the protocol to drive
//  Sierra's FastAPI + python-socketio backend in real time:
//
//    • connects to ws://host:port/socket.io/?EIO=4&transport=websocket
//    • completes the Engine.IO open + Socket.IO namespace connect handshake
//    • answers Engine.IO pings (2) with pongs (3) to keep the session alive
//    • emits events  ->  42["event", payload]
//    • decodes events <-  42["event", payload]
//
//  Backend event contracts (see backend/server.py):
//    status        {"msg": String}
//    error         {"msg": String}
//    transcription {"sender": "User"|"Sierra", "text": String}
//    audio_data    {"data": [Int]}   // raw 16-bit LE PCM, mono, 24 kHz
//    auth_status   {"authenticated": Bool}
//

import Foundation

final class SierraSocketClient: NSObject, URLSessionWebSocketDelegate {

    // MARK: Callbacks (always delivered on the main thread)
    var onStatus: ((String) -> Void)?
    var onTranscription: ((_ sender: String, _ text: String) -> Void)?
    var onAudio: ((Data) -> Void)?
    var onError: ((String) -> Void)?
    var onConnectedChange: ((Bool) -> Void)?
    var onAuthStatus: ((Bool) -> Void)?
    var onToolExecution: ((_ tool: String, _ realtime: Bool) -> Void)?

    private(set) var isConnected = false

    private let url: URL
    private var task: URLSessionWebSocketTask?
    private var pendingStartAudio = false
    private var shouldReconnect = true
    private var reconnectAttempts = 0
    private let maxReconnectDelay: Double = 30
    private lazy var session: URLSession = {
        URLSession(configuration: .default, delegate: self, delegateQueue: nil)
    }()

    init(host: String = "localhost", port: Int = 8000) {
        self.url = URL(string: "ws://\(host):\(port)/socket.io/?EIO=4&transport=websocket")!
        super.init()
    }

    // MARK: - Lifecycle
    func connect() {
        shouldReconnect = true
        guard task == nil else { return }
        let t = session.webSocketTask(with: url)
        task = t
        t.resume()
        receiveLoop()
    }

    func disconnect() {
        shouldReconnect = false       // stop auto-reconnecting
        sendRaw("41")                 // Socket.IO DISCONNECT
        task?.cancel(with: .goingAway, reason: nil)
        task = nil
        setConnected(false)
    }

    /// Reconnect after a capped exponential backoff, so the real-time link is
    /// always-on (God Mode) and survives a backend restart.
    private func scheduleReconnect() {
        guard shouldReconnect else { return }
        let delay = min(maxReconnectDelay, pow(2.0, Double(reconnectAttempts)))
        reconnectAttempts += 1
        deliver { $0.onStatus?(String(format: "Reconnecting in %.0fs…", delay)) }
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            guard let self, self.shouldReconnect, self.task == nil else { return }
            self.connect()
        }
    }

    // MARK: - High-level API
    /// Start the backend's real-time Gemini Live audio session.
    func startAudio() {
        if isConnected {
            emit("start_audio", ["source": "macos-native"])
        } else {
            pendingStartAudio = true   // fire as soon as the handshake completes
        }
    }

    func stopAudio() {
        pendingStartAudio = false
        emit("stop_audio")
    }

    // MARK: - Emit
    func emit(_ event: String, _ payload: Any? = nil) {
        var arr: [Any] = [event]
        if let payload { arr.append(payload) }
        guard let data = try? JSONSerialization.data(withJSONObject: arr),
              let json = String(data: data, encoding: .utf8) else { return }
        sendRaw("42" + json)           // 4 = message, 2 = EVENT
    }

    private func sendRaw(_ text: String) {
        task?.send(.string(text)) { [weak self] err in
            if let err { self?.deliver { $0.onError?("send failed: \(err.localizedDescription)") } }
        }
    }

    // MARK: - Receive
    private func receiveLoop() {
        task?.receive { [weak self] result in
            guard let self else { return }
            switch result {
            case .failure(let err):
                self.deliver { $0.onError?("socket closed: \(err.localizedDescription)") }
                self.setConnected(false)
                self.task = nil
                self.scheduleReconnect()
            case .success(let message):
                switch message {
                case .string(let text): self.handleEngineIO(text)
                case .data(let d):
                    if let text = String(data: d, encoding: .utf8) { self.handleEngineIO(text) }
                @unknown default: break
                }
                self.receiveLoop()
            }
        }
    }

    private func handleEngineIO(_ text: String) {
        guard let type = text.first else { return }
        let body = String(text.dropFirst())
        switch type {
        case "0": sendRaw("40")                 // open -> Socket.IO CONNECT (default ns)
        case "2": sendRaw("3")                  // ping -> pong
        case "3": break                          // pong
        case "4": handleSocketIO(body)           // message -> Socket.IO packet
        case "1": setConnected(false)            // close
        default: break
        }
    }

    private func handleSocketIO(_ packet: String) {
        guard let type = packet.first else { return }
        let body = String(packet.dropFirst())
        switch type {
        case "0":                                // CONNECT (handshake complete)
            reconnectAttempts = 0                // healthy link — reset backoff
            setConnected(true)
            if pendingStartAudio { pendingStartAudio = false; startAudio() }
        case "1": setConnected(false)            // DISCONNECT
        case "2": decodeEvent(body)              // EVENT
        case "4": deliver { $0.onError?("connect error: \(body)") }
        default: break
        }
    }

    private func decodeEvent(_ payload: String) {
        // An optional numeric ack id may precede the JSON array; skip to '['.
        guard let start = payload.firstIndex(of: "[") else { return }
        let json = String(payload[start...])
        guard let data = json.data(using: .utf8),
              let arr = try? JSONSerialization.jsonObject(with: data) as? [Any],
              let event = arr.first as? String else { return }
        let arg = arr.count > 1 ? arr[1] : nil
        dispatch(event, arg)
    }

    private func dispatch(_ event: String, _ arg: Any?) {
        let dict = arg as? [String: Any]
        switch event {
        case "status":
            if let msg = dict?["msg"] as? String { deliver { $0.onStatus?(msg) } }
        case "error":
            if let msg = dict?["msg"] as? String { deliver { $0.onError?(msg) } }
        case "auth_status":
            if let ok = dict?["authenticated"] as? Bool { deliver { $0.onAuthStatus?(ok) } }
        case "transcription":
            let sender = (dict?["sender"] as? String) ?? "Sierra"
            let text = (dict?["text"] as? String) ?? (arg as? String) ?? ""
            if !text.isEmpty { deliver { $0.onTranscription?(sender, text) } }
        case "tool_execution":
            let tool = (dict?["tool"] as? String) ?? "tool"
            let realtime = (dict?["realtime"] as? Bool) ?? true
            deliver { $0.onToolExecution?(tool, realtime) }
        case "audio_data":
            if let list = dict?["data"] as? [Int] {
                var bytes = [UInt8](); bytes.reserveCapacity(list.count)
                for v in list { bytes.append(UInt8(truncatingIfNeeded: v)) }
                let data = Data(bytes)
                deliver { $0.onAudio?(data) }
            }
        default:
            break
        }
    }

    // MARK: - Helpers
    private func setConnected(_ value: Bool) {
        guard isConnected != value else { return }
        isConnected = value
        deliver { $0.onConnectedChange?(value) }
    }

    private func deliver(_ block: @escaping (SierraSocketClient) -> Void) {
        DispatchQueue.main.async { [weak self] in if let self { block(self) } }
    }

    // MARK: - URLSessionWebSocketDelegate
    func urlSession(_ session: URLSession,
                    webSocketTask: URLSessionWebSocketTask,
                    didOpenWithProtocol protocol: String?) {
        // Engine.IO open packet arrives as the first message; handled there.
    }

    func urlSession(_ session: URLSession,
                    webSocketTask: URLSessionWebSocketTask,
                    didCloseWith closeCode: URLSessionWebSocketTask.CloseCode,
                    reason: Data?) {
        setConnected(false)
    }
}
