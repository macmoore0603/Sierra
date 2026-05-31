//
//  AudioStreamPlayer.swift
//  Sierra
//
//  Plays Sierra's real-time voice as it streams in. The backend emits
//  `audio_data` chunks of raw 16-bit little-endian PCM, mono, 24 kHz
//  (sierra.py: paInt16 / CHANNELS=1 / RECEIVE_SAMPLE_RATE=24000). Each chunk is
//  converted to float samples and scheduled on an AVAudioPlayerNode so playback
//  starts immediately and stays gap-free.
//

import Foundation
import AVFoundation

final class AudioStreamPlayer {

    private let engine = AVAudioEngine()
    private let player = AVAudioPlayerNode()
    private let sampleRate: Double = 24_000
    private let format: AVAudioFormat
    private var started = false

    init() {
        format = AVAudioFormat(commonFormat: .pcmFormatFloat32,
                               sampleRate: sampleRate,
                               channels: 1,
                               interleaved: false)!
        engine.attach(player)
        // Connect through the main mixer; it resamples 24 kHz -> the output device rate.
        engine.connect(player, to: engine.mainMixerNode, format: format)
    }

    /// Spin up the engine and begin playback. Safe to call repeatedly.
    func start() {
        guard !started else { return }
        engine.prepare()
        do {
            try engine.start()
            player.play()
            started = true
        } catch {
            print("[AudioStreamPlayer] engine start failed: \(error)")
        }
    }

    /// Stop playback and release the audio device.
    func stop() {
        guard started else { return }
        player.stop()
        engine.stop()
        started = false
    }

    /// Enqueue one streamed PCM16 chunk for immediate playback.
    func enqueue(_ pcm16: Data) {
        guard pcm16.count >= 2 else { return }
        if !started { start() }

        let sampleCount = pcm16.count / 2
        guard let buffer = AVAudioPCMBuffer(pcmFormat: format,
                                            frameCapacity: AVAudioFrameCount(sampleCount)) else { return }
        buffer.frameLength = AVAudioFrameCount(sampleCount)

        guard let channel = buffer.floatChannelData?[0] else { return }
        pcm16.withUnsafeBytes { (raw: UnsafeRawBufferPointer) in
            let samples = raw.bindMemory(to: Int16.self)
            for i in 0..<sampleCount {
                // little-endian Int16 -> normalized float [-1, 1]
                channel[i] = Float(Int16(littleEndian: samples[i])) / 32768.0
            }
        }

        player.scheduleBuffer(buffer, completionHandler: nil)
        if !player.isPlaying { player.play() }
    }
}
