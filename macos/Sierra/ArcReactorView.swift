//
//  ArcReactorView.swift
//  Sierra
//
//  A premium, always-alive arc reactor in black + metallic gold. Idles with a
//  slow spin and breathing glow; intensifies (faster, brighter, larger) while
//  Sierra is listening. Self-contained animation state so it stays alive on any
//  tab.
//

import SwiftUI

struct ArcReactorView: View {
    var isListening: Bool
    var size: CGFloat = 240

    @State private var spin: Double = 0
    @State private var counterSpin: Double = 0
    @State private var scale: CGFloat = 1.0
    @State private var glow: Double = 0.8

    var body: some View {
        ZStack {
            // Outer halo
            Circle()
                .fill(RadialGradient(colors: [Theme.gold.opacity(glow * 0.22), .clear],
                                     center: .center, startRadius: size * 0.18, endRadius: size * 0.62))

            // Outer tick ring (rotates slowly)
            tickRing(count: 60, length: size * 0.045, width: 1.5, color: Theme.gold.opacity(0.5))
                .frame(width: size * 0.98, height: size * 0.98)
                .rotationEffect(.degrees(spin))

            // Segmented dashed ring (counter-rotates)
            Circle()
                .stroke(Theme.metalGold,
                        style: StrokeStyle(lineWidth: 3, lineCap: .round, dash: [2, 14]))
                .frame(width: size * 0.86, height: size * 0.86)
                .rotationEffect(.degrees(counterSpin))
                .opacity(0.8)

            // Main glowing ring (breathes / pulses)
            Circle()
                .stroke(Theme.metalGold, lineWidth: size * 0.075)
                .frame(width: size * 0.7, height: size * 0.7)
                .scaleEffect(scale)
                .opacity(glow)
                .shadow(color: Theme.gold.opacity(0.7), radius: isListening ? 34 : 18)

            // Thin inner ring
            Circle()
                .stroke(Theme.gold.opacity(0.5), lineWidth: 1.5)
                .frame(width: size * 0.52, height: size * 0.52)
                .rotationEffect(.degrees(-counterSpin))

            // Core
            Circle()
                .fill(RadialGradient(colors: [Theme.goldLight, Theme.gold, Theme.goldDeep, .black],
                                     center: .center, startRadius: size * 0.02, endRadius: size * 0.26))
                .frame(width: size * 0.42, height: size * 0.42)
                .overlay(
                    Circle()
                        .fill(RadialGradient(colors: [.white.opacity(0.55), .clear],
                                             center: UnitPoint(x: 0.38, y: 0.34),
                                             startRadius: 1, endRadius: size * 0.16))
                )
                .shadow(color: Theme.gold.opacity(0.9), radius: 30)
                .scaleEffect(scale)

            Image(systemName: "sparkles")
                .font(.system(size: size * 0.12, weight: .bold))
                .foregroundStyle(.black.opacity(0.65))
        }
        .frame(width: size, height: size)
        .onAppear { animate(listening: isListening) }
        .onChange(of: isListening) { _, now in animate(listening: now) }
    }

    private func tickRing(count: Int, length: CGFloat, width: CGFloat, color: Color) -> some View {
        ZStack {
            ForEach(0..<count, id: \.self) { i in
                RoundedRectangle(cornerRadius: width)
                    .fill(color)
                    .frame(width: width, height: length)
                    .offset(y: -size * 0.46)
                    .rotationEffect(.degrees(Double(i) / Double(count) * 360))
            }
        }
    }

    private func animate(listening: Bool) {
        // breathing / pulsing
        withAnimation(.easeInOut(duration: listening ? 0.45 : 2.0).repeatForever(autoreverses: true)) {
            scale = listening ? 1.18 : 1.04
            glow = listening ? 1.0 : 0.82
        }
        // continuous spins — reset to 0 first so a speed change never jumps backwards
        spin = 0; counterSpin = 0
        withAnimation(.linear(duration: listening ? 6 : 26).repeatForever(autoreverses: false)) {
            spin = 360
        }
        withAnimation(.linear(duration: listening ? 9 : 38).repeatForever(autoreverses: false)) {
            counterSpin = -360
        }
    }
}
