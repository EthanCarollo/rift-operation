
import SwiftUI

struct SampleSlotView: View {
    let soundName: String
    let busId: Int
    @ObservedObject var soundManager: SoundManager
    @ObservedObject var soundTrigger = SoundTrigger.shared
    
    // Local state for hover/interactions
    @State private var isHovered: Bool = false
    @State private var showBindings: Bool = false
    
    var body: some View {
        let isPlaying = soundManager.activeBusIds.contains(busId) && soundManager.activeNodeNames[busId] == soundName
        let isLoading = soundManager.loadingBusIds.contains(busId)
        let bindingCount = soundTrigger.bindings.filter { $0.soundName == soundName }.count
        
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
            }
            
            Spacer()
            
            // Name
            Text(soundName)
                .font(.system(size: 10, weight: .medium, design: .monospaced))
                .lineLimit(2)
                .multilineTextAlignment(.center)
                .foregroundColor(.white.opacity(0.9))
            
            Spacer()
            
            // Controls
            HStack {
                Button(action: {
                    guard let node = findNode(name: soundName) else { return }
                    if isPlaying {
                        soundManager.stopSound(onBus: busId)
                    } else {
                        soundManager.playSound(node: node, onBus: busId)
                    }
                }) {
                    Image(systemName: isPlaying ? "stop.fill" : "play.fill")
                        .font(.system(size: 12))
                        .foregroundColor(isPlaying ? .red : .white)
                }
                .buttonStyle(.plain)
                .disabled(isLoading)
                
                Spacer()
                
                Button(action: {
                    // Logic to remove sound from this bus?
                    // Or open bindings?
                    showBindings.toggle()
                }) {
                    Image(systemName: "gearshape.fill")
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.5))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(6)
        .frame(width: 100, height: 80)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(Color(white: 0.15))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .stroke(isPlaying ? Color.green : Color.white.opacity(0.1), lineWidth: 1)
        )
        // Context Menu for management
        .contextMenu {
            Button("Remove from Bus") {
                // Implement removal logic - wait, SoundRoutes is 1-to-1 currently?
                // "soundRoutes: [String: Int]" -> One sound can only be on ONE bus.
                // So removing it sets route to 0.
                soundManager.soundRoutes[soundName] = 0
            }
            
            Button("Manage Bindings") {
                // Trigger binding modal/popover logic (TODO)
            }
        }
        .onHover { hover in isHovered = hover }
        .help("Sound: \(soundName)\nBus: \(busId)")
    }
    
    // Helper to find node
    private func findNode(name: String) -> SoundManager.FileNode? {
        return SoundManager.shared.getAllFiles().first(where: { $0.name == name })
    }
}
