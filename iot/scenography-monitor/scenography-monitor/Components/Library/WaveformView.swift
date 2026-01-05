
import SwiftUI
import AVFoundation

/// Caches waveform data to avoid recomputing
class WaveformCache {
    static let shared = WaveformCache()
    private var cache: [URL: [Float]] = [:]
    
    func getWaveform(for url: URL) -> [Float]? {
        return cache[url]
    }
    
    func setWaveform(_ samples: [Float], for url: URL) {
        cache[url] = samples
    }
}

/// A mini waveform visualization for audio files
struct WaveformView: View {
    let url: URL
    var tintColor: Color = Color.blue.opacity(0.6)
    let barCount: Int = 40
    let height: CGFloat = 24
    
    @State private var samples: [Float] = []
    @State private var isLoading: Bool = true
    
    var body: some View {
        HStack(alignment: .center, spacing: 1) {
            if isLoading {
                Rectangle()
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: height)
            } else if samples.isEmpty {
                // Fallback for failed loads
                Image(systemName: "waveform")
                    .font(.system(size: 10))
                    .foregroundColor(.secondary)
            } else {
                ForEach(0..<samples.count, id: \.self) { index in
                    RoundedRectangle(cornerRadius: 1)
                        .fill(tintColor)
                        .frame(width: 2, height: max(2, CGFloat(samples[index]) * height))
                }
            }
        }
        .frame(height: height)
        .onAppear {
            loadWaveform()
        }
    }
    
    private func loadWaveform() {
        // Check cache first
        if let cached = WaveformCache.shared.getWaveform(for: url) {
            self.samples = cached
            self.isLoading = false
            return
        }
        
        // Load in background
        DispatchQueue.global(qos: .utility).async {
            let waveformSamples = extractWaveform(from: url, barCount: barCount)
            
            DispatchQueue.main.async {
                self.samples = waveformSamples
                self.isLoading = false
                WaveformCache.shared.setWaveform(waveformSamples, for: url)
            }
        }
    }
}

/// Extracts downsampled waveform data from an audio file
private func extractWaveform(from url: URL, barCount: Int) -> [Float] {
    do {
        let file = try AVAudioFile(forReading: url)
        let format = file.processingFormat
        let frameCount = UInt32(file.length)
        
        guard frameCount > 0,
              let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frameCount) else {
            return []
        }
        
        try file.read(into: buffer)
        
        guard let floatData = buffer.floatChannelData else {
            return []
        }
        
        let channelData = floatData[0] // First channel
        let samplesPerBar = Int(frameCount) / barCount
        
        var result: [Float] = []
        
        for i in 0..<barCount {
            let start = i * samplesPerBar
            let end = min(start + samplesPerBar, Int(frameCount))
            
            // Calculate RMS for this segment
            var sum: Float = 0
            for j in start..<end {
                sum += abs(channelData[j])
            }
            let avg = sum / Float(end - start)
            result.append(min(avg * 4, 1.0)) // Scale up for visibility
        }
        
        return result
    } catch {
        print("Waveform extraction failed: \(error)")
        return []
    }
}
