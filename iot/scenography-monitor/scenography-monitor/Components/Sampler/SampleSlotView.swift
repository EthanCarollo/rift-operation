
import SwiftUI

struct SampleSlotView: View {
    let instance: SoundManager.SoundInstance
    let busId: Int
    @ObservedObject var soundManager: SoundManager
    @ObservedObject var soundTrigger = SoundTrigger.shared
    
    @State private var isHovered: Bool = false
    
    private let waveformHeight: CGFloat = 24
    
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
                Circle()
                    .fill(isPlaying ? Color.green : (isLoading ? Color.orange : Color.gray.opacity(0.3)))
                    .frame(width: 8, height: 8)
                
                Spacer()
                
                if bindingCount > 0 {
                    Text("\(bindingCount)")
                        .font(.system(size: 8, weight: .bold))
                        .padding(2)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .clipShape(Circle())
                }
                
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
            .fixedSize(horizontal: false, vertical: true)
            
            // Waveform with Progress Overlay
            if let url = fileURL {
                ZStack(alignment: .leading) {
                    // Full waveform (always blue)
                    WaveformView(url: url, tintColor: .blue.opacity(0.5))
                    
                    // Progress overlay (green, only visible when playing)
                    if isPlaying {
                        WaveformView(url: url, tintColor: .green)
                            .clipShape(
                                Rectangle()
                                    .size(width: 110 * CGFloat(progress), height: waveformHeight)
                            )
                        
                        // Playhead line
                        if progress > 0 {
                            Rectangle()
                                .fill(Color.white)
                                .frame(width: 2)
                                .offset(x: (110 - 12) * CGFloat(progress))
                        }
                    }
                }
                .frame(height: waveformHeight)
                .clipped()
            } else {
                // Fallback if file not found
                Rectangle()
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: waveformHeight)
                    .cornerRadius(4)
            }
            
            // Name
            Text(instance.filename)
                .font(.system(size: 9, weight: .medium, design: .monospaced))
                .lineLimit(1)
                .truncationMode(.middle)
                .foregroundColor(.white.opacity(0.9))
                .fixedSize(horizontal: false, vertical: true)
            
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
                .accessibilityIdentifier("SampleSlot_PlayButton_\(instance.id)")
                
                Spacer()
            }
            .fixedSize(horizontal: false, vertical: true)
        }
        .padding(6)
        .frame(width: 110)
        .fixedSize(horizontal: true, vertical: true)
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
