//
//  Theme.swift
//  Sierra
//
//  Black + metallic-gold JARVIS theme: shared colors, gradients and helpers.
//

import SwiftUI

extension Color {
    init(hex: UInt, alpha: Double = 1) {
        self.init(.sRGB,
                  red: Double((hex >> 16) & 0xff) / 255,
                  green: Double((hex >> 8) & 0xff) / 255,
                  blue: Double(hex & 0xff) / 255,
                  opacity: alpha)
    }
}

enum Theme {
    // Backgrounds — near-black with a warm undertone
    static let bg0 = Color(hex: 0x000000)
    static let bg1 = Color(hex: 0x0E0B05)
    static let bg2 = Color(hex: 0x1A1206)
    static let panel = Color(hex: 0x140F07)

    // Gold ramp
    static let goldLight = Color(hex: 0xFCE7B4)
    static let gold = Color(hex: 0xE9C257)
    static let goldDeep = Color(hex: 0xB8860B)
    static let goldBronze = Color(hex: 0x7A5A16)

    static let textPrimary = Color(hex: 0xF3E8C8)
    static let textDim = Color(hex: 0x9A8A63)

    /// Background gradient for the whole window.
    static let backdrop = LinearGradient(
        colors: [bg0, bg2, bg0],
        startPoint: .topLeading, endPoint: .bottomTrailing)

    /// Brushed-metal gold sheen for wordmarks, rings and accents.
    static let metalGold = LinearGradient(
        colors: [goldLight, gold, goldDeep, gold, goldLight],
        startPoint: .topLeading, endPoint: .bottomTrailing)

    static let goldStroke = LinearGradient(
        colors: [gold.opacity(0.9), goldDeep.opacity(0.5)],
        startPoint: .top, endPoint: .bottom)

    /// Hairline gold border + faint fill used by cards/panels.
    static func panelStroke(_ opacity: Double = 0.35) -> LinearGradient {
        LinearGradient(colors: [gold.opacity(opacity), goldBronze.opacity(opacity * 0.6)],
                       startPoint: .topLeading, endPoint: .bottomTrailing)
    }
}

/// A reusable dark panel with a hairline gold border and soft glow.
struct GoldPanel<Content: View>: View {
    var padding: CGFloat = 16
    @ViewBuilder var content: () -> Content
    var body: some View {
        content()
            .padding(padding)
            .background(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(Theme.panel.opacity(0.85))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .strokeBorder(Theme.panelStroke(), lineWidth: 1)
            )
            .shadow(color: Theme.gold.opacity(0.08), radius: 12, y: 4)
    }
}
