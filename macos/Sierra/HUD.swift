//
//  HUD.swift
//  Sierra
//
//  The JARVIS HUD chrome — God Mode status pills and the mirrored audio bar —
//  rebuilt in black + metallic gold (ported from the original cyan web HUD:
//  GodModeStatusPills.jsx + TopAudioBar.jsx).
//

import SwiftUI

// MARK: - God Mode status pills (⚡ DAEMON · 🎤 HEY SIERRA · ✋ GESTURES · 👁 PRESENCE)

struct StatusPills: View {
    let connected: Bool
    let listening: Bool

    var body: some View {
        HStack(spacing: 8) {
            pill("⚡", "DAEMON", connected ? "GOD" : "LINK…", bright: true)
            pill("🎤", "HEY SIERRA", listening ? "LISTENING" : "LIVE", bright: listening)
            pill("✋", "GESTURES", "GOD", bright: false)
            pill("👁", "PRESENCE", "PRESENT", bright: false)
        }
    }

    private func pill(_ glyph: String, _ name: String, _ value: String, bright: Bool) -> some View {
        HStack(spacing: 5) {
            Text(glyph).font(.system(size: 11))
            Text("\(name): \(value)")
                .font(.system(size: 11, weight: .bold, design: .rounded))
        }
        .foregroundColor(.black)
        .padding(.horizontal, 11)
        .padding(.vertical, 6)
        .background(
            Capsule().fill(bright ? AnyShapeStyle(Theme.metalGold)
                                  : AnyShapeStyle(LinearGradient(colors: [Theme.goldDeep, Theme.goldBronze],
                                                                 startPoint: .top, endPoint: .bottom)))
        )
        .overlay(Capsule().strokeBorder(Theme.goldLight.opacity(0.35), lineWidth: 0.5))
        .shadow(color: Theme.gold.opacity(bright ? 0.6 : 0.18), radius: bright ? 8 : 3)
    }
}

// MARK: - Mirrored audio bar visualizer

struct TopAudioBar: View {
    var active: Bool

    var body: some View {
        TimelineView(.animation) { timeline in
            Canvas { ctx, size in
                let t = timeline.date.timeIntervalSinceReferenceDate
                let barW: CGFloat = 3
                let gap: CGFloat = 3
                let half = Int(size.width / (2 * (barW + gap)))
                let center = size.width / 2
                let speed = active ? 7.0 : 2.6
                let amp = active ? 0.92 : 0.32

                for i in 0..<half {
                    // layered sines give an organic, mirrored waveform
                    let phase = Double(i) * 0.45 + t * speed
                    let v = ((sin(phase) * 0.6 + sin(phase * 0.5 + 1.3) * 0.4) * 0.5 + 0.5) * amp
                    let falloff = 1.0 - Double(i) / Double(max(half, 1)) * 0.5
                    let h = max(2, CGFloat(v * falloff) * size.height)
                    let y = (size.height - h) / 2
                    let opacity = 0.28 + v * 0.72

                    let r = CGRect(x: center + CGFloat(i) * (barW + gap), y: y, width: barW, height: h)
                    let l = CGRect(x: center - CGFloat(i + 1) * (barW + gap), y: y, width: barW, height: h)
                    ctx.fill(Path(roundedRect: r, cornerRadius: 1.5), with: .color(Theme.gold.opacity(opacity)))
                    ctx.fill(Path(roundedRect: l, cornerRadius: 1.5), with: .color(Theme.gold.opacity(opacity)))
                }
            }
        }
        .frame(height: 34)
    }
}
