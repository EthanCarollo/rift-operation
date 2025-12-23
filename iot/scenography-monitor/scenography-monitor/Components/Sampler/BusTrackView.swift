
import SwiftUI
import UniformTypeIdentifiers

struct BusTrackView: View {
    let bus: SoundManager.AudioBus
    @ObservedObject var soundManager: SoundManager
    
    // Binding for dropped items
    @State private var isTargeted: Bool = false
    
    var body: some View {
        HStack(spacing: 0) {
            // Bus Control Header (Left)
            ZStack {
                Rectangle()
                    .fill(Color(hex: bus.colorHex).opacity(0.1))
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(bus.name.uppercased())
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(hex: bus.colorHex))
                    
                    HStack {
                        // Mute / Solo
                        Button(action: { soundManager.toggleMute(onBus: bus.id) }) {
                            Text("M")
                                .font(.system(size: 8, weight: .bold))
                                .frame(width: 16, height: 16)
                                .background(bus.isMuted ? Color.orange : Color.gray.opacity(0.2))
                                .foregroundColor(.white)
                                .cornerRadius(2)
                        }.buttonStyle(.plain)
                        
                        Button(action: { soundManager.toggleSolo(onBus: bus.id) }) {
                            Text("S")
                                .font(.system(size: 8, weight: .bold))
                                .frame(width: 16, height: 16)
                                .background(bus.isSolo ? Color.green : Color.gray.opacity(0.2))
                                .foregroundColor(.white)
                                .cornerRadius(2)
                        }.buttonStyle(.plain)
                    }
                    
                    // Volume Slider (Mini)
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            Rectangle().fill(Color.gray.opacity(0.2))
                            Rectangle().fill(Color(hex: bus.colorHex))
                                .frame(width: geo.size.width * CGFloat(bus.volume))
                        }
                    }
                    .frame(height: 4)
                    .padding(.trailing, 8)
                }
                .padding(6)
            }
            .frame(width: 100)
            .border(Color.gray.opacity(0.2), width: 1, edges: [.trailing])
            
            // Track Area (Droppable)
            ZStack(alignment: .leading) {
                // Background
                Rectangle()
                    .fill(isTargeted ? Color.blue.opacity(0.1) : Color.black.opacity(0.2))
                
                // Content: Horizontal Stack of Slots
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        // Filter sounds assigned to this bus
                        let assignedSounds = soundManager.soundRoutes
                            .filter { $0.value == bus.id }
                            .map { $0.key }
                            .sorted()
                        
                        ForEach(assignedSounds, id: \.self) { soundName in
                            SampleSlotView(soundName: soundName, busId: bus.id, soundManager: soundManager)
                        }
                        
                        // Empty Slot hint if empty
                        if assignedSounds.isEmpty {
                            Text("Drop Sounds Here")
                                .font(.system(size: 10, design: .monospaced))
                                .foregroundColor(.gray.opacity(0.4))
                                .padding(.leading, 10)
                        }
                    }
                    .padding(8)
                }
            }
            .onDrop(of: [.text], isTargeted: $isTargeted) { providers in
                providers.first?.loadObject(ofClass: String.self) { (str, error) in
                    guard let soundName = str else { return }
                    DispatchQueue.main.async {
                        // Assign logic
                        // Remove from old bus (implicitly handled by map replacement)
                        soundManager.soundRoutes[soundName] = bus.id
                        print("Dropped \(soundName) on Bus \(bus.id)")
                    }
                }
                return true
            }
        }
        .frame(height: 100)
        .background(Color(nsColor: .controlBackgroundColor))
        .border(Color.gray.opacity(0.2), width: 1, edges: [.bottom])
    }
}


