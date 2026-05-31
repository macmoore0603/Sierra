//
//  JarvisHUD.swift
//  Sierra
//
//  Immersive Stark/JARVIS-style HUD in black + metallic gold: a central
//  triangular arc reactor ringed by rotating arcs, surrounded by dense telemetry
//  panels, animated spectrum/line graphs, a live clock + system readout, the chat
//  log, and a branded footer.
//

import SwiftUI

// MARK: - Shapes

struct TriangleShape: Shape {
    var pointDown = true
    func path(in r: CGRect) -> Path {
        var p = Path()
        if pointDown {
            p.move(to: CGPoint(x: r.minX, y: r.minY))
            p.addLine(to: CGPoint(x: r.maxX, y: r.minY))
            p.addLine(to: CGPoint(x: r.midX, y: r.maxY))
        } else {
            p.move(to: CGPoint(x: r.midX, y: r.minY))
            p.addLine(to: CGPoint(x: r.maxX, y: r.maxY))
            p.addLine(to: CGPoint(x: r.minX, y: r.maxY))
        }
        p.closeSubpath()
        return p
    }
}

// MARK: - Panel container (titled, bracketed)

struct HUDPanel<Content: View>: View {
    let title: String
    var minHeight: CGFloat? = nil
    @ViewBuilder var content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Rectangle().fill(Theme.gold).frame(width: 10, height: 2)
                Text(title.uppercased())
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .tracking(2)
                    .foregroundColor(Theme.gold)
                Spacer()
                Circle().stroke(Theme.gold.opacity(0.6), lineWidth: 1).frame(width: 6, height: 6)
            }
            content()
            Spacer(minLength: 0)
        }
        .padding(10)
        .frame(maxWidth: .infinity, minHeight: minHeight, alignment: .topLeading)
        .background(RoundedRectangle(cornerRadius: 8).fill(Theme.bg1.opacity(0.55)))
        .overlay(RoundedRectangle(cornerRadius: 8).strokeBorder(Theme.gold.opacity(0.28), lineWidth: 1))
        .overlay(alignment: .topLeading) { corner }
        .overlay(alignment: .bottomTrailing) { corner.rotationEffect(.degrees(180)) }
    }

    private var corner: some View {
        Path { p in
            p.move(to: CGPoint(x: 0, y: 8)); p.addLine(to: .zero); p.addLine(to: CGPoint(x: 8, y: 0))
        }
        .stroke(Theme.gold.opacity(0.8), lineWidth: 1.5)
        .frame(width: 8, height: 8)
        .padding(3)
    }
}

struct HUDStat: View {
    let label: String
    let value: String
    var body: some View {
        HStack {
            Text(label).font(.system(size: 10, weight: .medium, design: .monospaced))
                .foregroundColor(Theme.textDim)
            Spacer()
            Text(value).font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(Theme.textPrimary)
        }
    }
}

// MARK: - Live telemetry

struct TelemetryPanel: View {
    let connected: Bool
    let listening: Bool

    var body: some View {
        TimelineView(.periodic(from: .now, by: 1)) { ctx in
            let now = ctx.date
            HUDPanel(title: "Sierra OS · Telemetry") {
                VStack(spacing: 5) {
                    HStack(alignment: .firstTextBaseline) {
                        Text(timeString(now))
                            .font(.system(size: 26, weight: .heavy, design: .monospaced))
                            .foregroundStyle(Theme.metalGold)
                        Spacer()
                        Text(dateString(now))
                            .font(.system(size: 10, weight: .semibold, design: .monospaced))
                            .foregroundColor(Theme.textDim)
                    }
                    Divider().overlay(Theme.gold.opacity(0.15))
                    HUDStat(label: "LINK", value: connected ? "● GOD MODE" : "○ LINKING")
                    HUDStat(label: "VOICE", value: listening ? "LISTENING" : "STANDBY")
                    HUDStat(label: "HOST", value: host)
                    HUDStat(label: "CORES", value: "\(ProcessInfo.processInfo.activeProcessorCount)")
                    HUDStat(label: "MEMORY", value: memory)
                    HUDStat(label: "UPTIME", value: uptime)
                    HUDStat(label: "THERMAL", value: thermal)
                    HUDStat(label: "POWER", value: ProcessInfo.processInfo.isLowPowerModeEnabled ? "LOW-POWER" : "NOMINAL")
                }
            }
        }
    }

    private func timeString(_ d: Date) -> String {
        let f = DateFormatter(); f.dateFormat = "HH:mm:ss"; return f.string(from: d)
    }
    private func dateString(_ d: Date) -> String {
        let f = DateFormatter(); f.dateFormat = "EEE dd MMM yyyy"; return f.string(from: d).uppercased()
    }
    private var host: String {
        ProcessInfo.processInfo.hostName.replacingOccurrences(of: ".local", with: "")
    }
    private var memory: String {
        String(format: "%.0f GB", Double(ProcessInfo.processInfo.physicalMemory) / 1_073_741_824)
    }
    private var uptime: String {
        let s = Int(ProcessInfo.processInfo.systemUptime)
        return "\(s / 3600)h \((s % 3600) / 60)m"
    }
    private var thermal: String {
        switch ProcessInfo.processInfo.thermalState {
        case .nominal: return "NOMINAL"
        case .fair: return "FAIR"
        case .serious: return "SERIOUS"
        case .critical: return "CRITICAL"
        @unknown default: return "—"
        }
    }
}

// MARK: - Animated graphs

struct SpectrumGraph: View {
    var active: Bool
    var body: some View {
        TimelineView(.animation) { tl in
            Canvas { ctx, size in
                let t = tl.date.timeIntervalSinceReferenceDate
                let bw: CGFloat = 4, gap: CGFloat = 3
                let n = max(1, Int(size.width / (bw + gap)))
                let speed = active ? 6.0 : 2.4
                let amp = active ? 0.95 : 0.4
                for i in 0..<n {
                    let ph = Double(i) * 0.5 + t * speed
                    let v = ((sin(ph) * 0.6 + sin(ph * 0.37 + 1.1) * 0.4) * 0.5 + 0.5) * amp
                    let h = max(2, CGFloat(v) * size.height)
                    let rect = CGRect(x: CGFloat(i) * (bw + gap), y: size.height - h, width: bw, height: h)
                    ctx.fill(Path(roundedRect: rect, cornerRadius: 1), with: .color(Theme.gold.opacity(0.35 + v * 0.65)))
                }
            }
        }
    }
}

struct LineGraph: View {
    var seed: Double = 0
    var body: some View {
        TimelineView(.animation) { tl in
            Canvas { ctx, size in
                let t = tl.date.timeIntervalSinceReferenceDate + seed
                var path = Path()
                let steps = 48
                for s in 0...steps {
                    let x = size.width * CGFloat(s) / CGFloat(steps)
                    let ph = Double(s) * 0.32 + t * 1.6 + seed
                    let v = sin(ph) * 0.34 + sin(ph * 0.5 + 0.7) * 0.16 + 0.5
                    let y = size.height * (1 - CGFloat(v))
                    if s == 0 { path.move(to: CGPoint(x: x, y: y)) } else { path.addLine(to: CGPoint(x: x, y: y)) }
                }
                ctx.stroke(path, with: .color(Theme.gold.opacity(0.85)), lineWidth: 1.5)
                // baseline grid
                for g in 1..<4 {
                    let y = size.height * CGFloat(g) / 4
                    ctx.stroke(Path { p in p.move(to: CGPoint(x: 0, y: y)); p.addLine(to: CGPoint(x: size.width, y: y)) },
                               with: .color(Theme.gold.opacity(0.08)), lineWidth: 0.5)
                }
            }
        }
    }
}

// MARK: - Triangular reactor

struct TriReactor: View {
    var listening: Bool
    var size: CGFloat = 260

    @State private var spin: Double = 0
    @State private var counter: Double = 0
    @State private var pulse: CGFloat = 1
    @State private var glow: Double = 0.8

    var body: some View {
        ZStack {
            Circle()
                .fill(RadialGradient(colors: [Theme.gold.opacity(glow * 0.22), .clear],
                                     center: .center, startRadius: size * 0.1, endRadius: size * 0.6))

            // rotating tick ring
            ForEach(0..<72, id: \.self) { i in
                RoundedRectangle(cornerRadius: 1)
                    .fill(Theme.gold.opacity(i % 6 == 0 ? 0.8 : 0.35))
                    .frame(width: 1.5, height: i % 6 == 0 ? size * 0.05 : size * 0.03)
                    .offset(y: -size * 0.47)
                    .rotationEffect(.degrees(Double(i) / 72 * 360 + spin))
            }

            // partial arcs
            Circle().trim(from: 0.05, to: 0.32)
                .stroke(Theme.metalGold, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                .frame(width: size * 0.86, height: size * 0.86)
                .rotationEffect(.degrees(counter))
            Circle().trim(from: 0.55, to: 0.78)
                .stroke(Theme.metalGold, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                .frame(width: size * 0.86, height: size * 0.86)
                .rotationEffect(.degrees(counter))
            Circle().stroke(Theme.gold.opacity(0.25), lineWidth: 1)
                .frame(width: size * 0.7, height: size * 0.7)
                .rotationEffect(.degrees(-counter * 1.4))

            // glowing triangle core (Mark-VII style, point down)
            TriangleShape(pointDown: true)
                .fill(RadialGradient(colors: [Theme.goldLight, Theme.gold, Theme.goldDeep],
                                     center: .center, startRadius: 2, endRadius: size * 0.22))
                .frame(width: size * 0.46, height: size * 0.4)
                .overlay(
                    TriangleShape(pointDown: true)
                        .stroke(Theme.goldLight, lineWidth: 2)
                        .frame(width: size * 0.3, height: size * 0.26)
                )
                .shadow(color: Theme.gold.opacity(0.9), radius: 28)
                .scaleEffect(pulse)

            TriangleShape(pointDown: true)
                .stroke(Theme.gold.opacity(0.5), lineWidth: 1.5)
                .frame(width: size * 0.62, height: size * 0.54)
                .rotationEffect(.degrees(spin * 0.2))
        }
        .frame(width: size, height: size)
        .onAppear { animate() }
        .onChange(of: listening) { _, _ in animate() }
    }

    private func animate() {
        withAnimation(.easeInOut(duration: listening ? 0.5 : 2.2).repeatForever(autoreverses: true)) {
            pulse = listening ? 1.14 : 1.03
            glow = listening ? 1.0 : 0.8
        }
        spin = 0; counter = 0
        withAnimation(.linear(duration: listening ? 8 : 30).repeatForever(autoreverses: false)) { spin = 360 }
        withAnimation(.linear(duration: listening ? 12 : 44).repeatForever(autoreverses: false)) { counter = -360 }
    }
}

// MARK: - The HUD

struct JarvisHUD: View {
    @ObservedObject var vm: SierraViewModel
    @Binding var inputText: String
    @FocusState private var focused: Bool

    var body: some View {
        VStack(spacing: 10) {
            HStack(alignment: .top, spacing: 12) {
                // Left column — telemetry + spectrum
                VStack(spacing: 10) {
                    TelemetryPanel(connected: vm.isConnected, listening: vm.isListening)
                    HUDPanel(title: "Audio Spectrum", minHeight: 90) {
                        SpectrumGraph(active: vm.isListening).frame(height: 60)
                    }
                }
                .frame(width: 230)

                // Center — reactor
                VStack(spacing: 10) {
                    Spacer(minLength: 0)
                    TriReactor(listening: vm.isListening, size: 250)
                        .onTapGesture { vm.toggleVoice() }
                    Text(vm.isListening ? "LISTENING" : (vm.isConnected ? "READY" : "OFFLINE"))
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .tracking(5)
                        .foregroundStyle(Theme.metalGold)
                    if !vm.liveTranscription.isEmpty {
                        Text(vm.liveTranscription)
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(Theme.gold)
                            .multilineTextAlignment(.center)
                            .lineLimit(2)
                    } else {
                        Text("◣ TAP REACTOR OR SAY “HEY SIERRA” ◢")
                            .font(.system(size: 9, weight: .medium, design: .monospaced))
                            .tracking(2)
                            .foregroundColor(Theme.textDim)
                    }
                    Spacer(minLength: 0)
                }
                .frame(maxWidth: .infinity)

                // Right column — chat log + signal graphs
                VStack(spacing: 10) {
                    HUDPanel(title: "Comms Log") {
                        chatLog
                    }
                    HUDPanel(title: "Signal", minHeight: 80) {
                        LineGraph(seed: 2.0).frame(height: 52)
                    }
                }
                .frame(width: 280)
            }
            .frame(maxHeight: .infinity)

            inputBar
            footer
        }
        .padding(16)
        .onAppear { if !inputText.isEmpty { focused = true } }
    }

    private var chatLog: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 10) {
                    if vm.messages.isEmpty {
                        Text("Awaiting input…")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(Theme.textDim)
                            .padding(.top, 8)
                    }
                    ForEach(vm.messages) { msg in
                        ChatBubble(text: msg.text, isUser: msg.isUser).id(msg.id)
                    }
                }
                .padding(.vertical, 4)
            }
            .frame(height: 230)
            .onChange(of: vm.messages.last?.id) { _, _ in scrollEnd(proxy) }
            .onChange(of: vm.messages.last?.text) { _, _ in scrollEnd(proxy) }
        }
    }

    private var inputBar: some View {
        HStack(spacing: 12) {
            TextField("Command Sierra…", text: $inputText)
                .textFieldStyle(.plain)
                .focused($focused)
                .font(.system(size: 13, design: .monospaced))
                .foregroundColor(Theme.textPrimary)
                .padding(.horizontal, 16).padding(.vertical, 11)
                .background(Capsule().fill(Theme.panel.opacity(0.9)))
                .overlay(Capsule().strokeBorder(Theme.goldStroke, lineWidth: 1.4))
                .onSubmit(send)
            Button(action: vm.toggleVoice) {
                Image(systemName: vm.isListening ? "stop.fill" : "mic.fill")
                    .font(.system(size: 16, weight: .bold)).foregroundColor(.black)
                    .frame(width: 42, height: 42)
                    .background(Circle().fill(vm.isListening ? AnyShapeStyle(Color(hex: 0xC0392B)) : AnyShapeStyle(Theme.metalGold)))
                    .shadow(color: (vm.isListening ? Color.red : Theme.gold).opacity(0.6), radius: 10)
            }.buttonStyle(.plain)
            Button(action: send) {
                Image(systemName: "paperplane.fill").font(.title3).foregroundStyle(Theme.metalGold)
            }.buttonStyle(.plain)
        }
    }

    private var footer: some View {
        HStack {
            Text("SIERRA").font(.system(size: 11, weight: .heavy, design: .monospaced))
                .tracking(4).foregroundStyle(Theme.metalGold)
            Text("// LEXUS NEXUS CAPITAL")
                .font(.system(size: 9, weight: .medium, design: .monospaced))
                .tracking(2).foregroundColor(Theme.textDim)
            Spacer()
            Text(vm.serverStatus.uppercased())
                .font(.system(size: 9, weight: .bold, design: .monospaced))
                .tracking(2).foregroundColor(Theme.textDim)
        }
        .padding(.horizontal, 4)
    }

    private func send() {
        let t = inputText; inputText = ""; vm.send(t)
    }
    private func scrollEnd(_ proxy: ScrollViewProxy) {
        guard let id = vm.messages.last?.id else { return }
        withAnimation(.easeOut(duration: 0.25)) { proxy.scrollTo(id, anchor: .bottom) }
    }
}
