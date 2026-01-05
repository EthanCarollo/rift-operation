
import SwiftUI

struct SampleSlotView: View {
    let instance: SoundManager.SoundInstance
    let busId: Int
    @ObservedObject var soundManager: SoundManager
    @ObservedObject var soundTrigger = SoundTrigger.shared
    
    @State private var isHovered: Bool = false
    
    var body: some View {
        let isPlaying = soundManager.activeInstanceIds.contains(instance.id)
        let isLoading = soundManager.loadingInstanceIds.contains(instance.id)
        let bindingCount = soundTrigger.bindings.filter { $0.instanceId == instance.id }.count
        let isSelected = soundManager.selectedInstanceId == instance.id
        let progress = soundManager.playbackProgress[instance.id] ?? 0
        
        // Get file URL for waveform
        let fileURL = soundManager.getAllFiles().first(where: { $0.name == instance.filename })?.url
        
        VStack(spacing: 2) {
            // Header / Status
            HStack {
                // Play Status Indicator
                Circle()
                    .fill(isPlaying ? Color.green : (isLoading ? Color.orange : Color.gray.opacity(0.3)))
                    .frame(width: 8, height: 8)
                
                Spacer()
                
                // Binding Badge
                if bindingCount > 0 {
                    Text("\(bindingCount)")
                        .font(.system(size: 8, weight: .bold))
                        .padding(2)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .clipShape(Circle())
                }
                
                // Remove Button
                Button(action: {
                    soundManager.removeInstance(instance.id, fromBus: busId)
                    if isSelected { soundManager.selectedInstanceId = nil }
                }) {
                    Image(systemName: "xmark")
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                }
                .buttonStyle(.plain)
                .padding(.leading, 4)
            }
            
            // Waveform with Progress Overlay
            if let url = fileURL {
                ZStack(alignment: .leading) {
                    // Waveform background
                    WaveformView(url: url, tintColor: .white.opacity(0.3))
                        .frame(height: 24)
                    
                    // Progress overlay (filled waveform)
                    WaveformView(url: url, tintColor: isPlaying ? .green : .blue.opacity(0.6))
                        .frame(height: 24)
                        .mask(
                            GeometryReader { geo in
                                Rectangle()
                                    .frame(width: geo.size.width * CGFloat(progress))
                            }
                        )
                    
                    // Playhead line
                    if isPlaying && progress > 0 {
                        GeometryReader { geo in
                            Rectangle()
                                .fill(Color.white)
                                .frame(width: 2, height: 24)
                                .offset(x: geo.size.width * CGFloat(progress) - 1)
                        }
                    }
                }
                .cornerRadius(4)
            }
            
            // Name
            Text(instance.filename)
                .font(.system(size: 9, weight: .medium, design: .monospaced))
                .lineLimit(1)
                .truncationMode(.middle)
                .foregroundColor(.white.opacity(0.9))
            
            // Controls
            HStack {
                Button(action: {
                    if isPlaying {
                        soundManager.stopSound(instanceID: instance.id)
                    } else {
                        soundManager.playSound(instance: instance, onBus: busId)
                    }
                }) {
                    Image(systemName: isPlaying ? "stop.fill" : "play.fill")
                        .font(.system(size: 12))
                        .foregroundColor(isPlaying ? .red : .white)
                }
                .buttonStyle(.plain)
                .disabled(isLoading)
                
                Spacer()
            }
        }
        .padding(6)
        .frame(width: 110, height: 100)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(isSelected ? Color.blue.opacity(0.3) : Color(white: 0.15))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .stroke(isSelected ? Color.blue : (isPlaying ? Color.green : (isHovered ? Color.white.opacity(0.3) : Color.white.opacity(0.1))), lineWidth: isSelected ? 2 : 1)
        )
        .onHover { hover in isHovered = hover }
        .onTapGesture {
            soundManager.selectedInstanceId = instance.id
        }
        .help("Sound: \(instance.filename)\nInstance: \(instance.id)")
    }
}
