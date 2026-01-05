
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
        let bindingCount = soundTrigger.bindings.filter { $0.instanceId == instance.id }.count // Filter by Instance ID
        let isSelected = soundManager.selectedInstanceId == instance.id
        
        VStack(spacing: 4) {
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
                
                // Remove Button (Small X)
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
            
            Spacer()
            
            // Name
            Text(instance.filename)
                .font(.system(size: 10, weight: .medium, design: .monospaced))
                .lineLimit(2)
                .multilineTextAlignment(.center)
                .foregroundColor(.white.opacity(0.9))
            
            Spacer()
            
            // Controls
            HStack {
                Button(action: {
                    if isPlaying {
                        // Stop specific instance
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
                
                // Select Button (Hidden hit area or explicit)
                // Actually the whole background will select.
                // Just showing play logic here.
            }
        }
        .padding(6)
        .frame(width: 100, height: 90)
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
