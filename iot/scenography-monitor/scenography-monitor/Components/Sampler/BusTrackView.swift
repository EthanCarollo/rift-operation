
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

                        
                        // Output Route Picker
                        Menu {
                            ForEach(soundManager.availableOutputs, id: \.self) { outputName in
                                Button(outputName) {
                                    // Map Name to UID? SoundManager needs a helper or we check `availableOutputDevices`
                                    // Currently `availableOutputs` is just strings. 
                                    // Ideally SoundManager exposes struct or we just pass name if it's unique enough (it is usually).
                                    // Actually SoundManager has `setOutputDevice(uid:name:...)`.
                                    // I need UID. `SoundManager` keeps `availableOutputDevices` private.
                                    // I should just pass name and let manager resolve, or ask manager to expose UIDs.
                                    // For now, let's assume `outputName` serves as key or update SoundManager to handle name lookup.
                                    // Wait, I can't access `availableOutputDevices` from here.
                                    // I will update SoundManager to correct this in a sec if needed, 
                                    // but `availableOutputs` (Strings) is what I have.
                                    // I'll call a new helper `setOutputDevice(name: ...)` or similar.
                                    // Let's assume `setOutputDevice(name: ...)` exists or I add it.
                                    soundManager.selectOutput(name: outputName, forBus: bus.id)
                                }
                            }
                        } label: {
                            Image(systemName: "arrow.triangle.branch")
                                .font(.system(size: 8))
                                .foregroundColor(.secondary)
                        }
                        .menuStyle(.borderlessButton)
                        .frame(width: 16)
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
                        // Get Instances for this Bus
                        let instances = soundManager.busSamples[bus.id] ?? []
                        
                        ForEach(instances) { instance in
                            SampleSlotView(instance: instance, busId: bus.id, soundManager: soundManager)
                        }
                        
                        // Empty Slot hint if empty
                        if instances.isEmpty {
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
                        // Add Instance Logic
                        // Decoupled Drag: Dropping here creates a new instance on this bus.
                        // It does NOT remove it from elsewhere (unless we implemented moving).
                        // Since drag source is 'Library', it's a Copy/Create operation.
                        soundManager.addInstance(filename: soundName, toBus: bus.id)
                        print("Added instance of \(soundName) to Bus \(bus.id)")
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
