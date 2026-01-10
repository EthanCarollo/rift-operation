
import SwiftUI
import UniformTypeIdentifiers

struct BusTrackView: View {
    let bus: SoundManager.AudioBus
    @ObservedObject var soundManager: SoundManager
    
    // Binding for dropped items
    @State private var isTargeted: Bool = false
    @State private var isEditingName: Bool = false
    @State private var editedName: String = ""
    @State private var showColorPicker: Bool = false
    @State private var selectedColor: Color = .white
    
    // Predefined color palette for quick selection
    private let colorPalette: [(name: String, hex: String)] = [
        ("Red", "#E57373"),
        ("Pink", "#F06292"),
        ("Purple", "#BA68C8"),
        ("Deep Purple", "#9575CD"),
        ("Indigo", "#7986CB"),
        ("Blue", "#64B5F6"),
        ("Cyan", "#4DD0E1"),
        ("Teal", "#4DB6AC"),
        ("Green", "#81C784"),
        ("Light Green", "#AED581"),
        ("Yellow", "#FFF176"),
        ("Orange", "#FFB74D"),
        ("Deep Orange", "#FF8A65"),
        ("Brown", "#A1887F"),
        ("Grey", "#90A4AE"),
        ("White", "#F0F0F0")
    ]
    
    var body: some View {
        HStack(spacing: 0) {
            // Bus Control Header (Left)
            ZStack {
                Rectangle()
                    .fill(Color(hex: bus.colorHex).opacity(0.1))
                
                VStack(alignment: .leading, spacing: 4) {
                    // Editable Bus Name
                    if isEditingName {
                        TextField("Bus Name", text: $editedName, onCommit: {
                            if !editedName.isEmpty {
                                soundManager.setBusName(editedName, onBus: bus.id)
                            }
                            isEditingName = false
                        })
                        .textFieldStyle(.plain)
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(Color(hex: bus.colorHex))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .accessibilityIdentifier("BusNameField_\(bus.id)")
                    } else {
                        Text(bus.name.uppercased())
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .foregroundColor(Color(hex: bus.colorHex))
                            .onTapGesture(count: 2) {
                                editedName = bus.name
                                isEditingName = true
                            }
                            .accessibilityIdentifier("BusNameLabel_\(bus.id)")
                    }
                    
                    HStack {
                        // Mute / Solo
                        Button(action: { soundManager.toggleMute(onBus: bus.id) }) {
                            Text("M")
                                .font(.system(size: 8, weight: .bold))
                                .frame(width: 16, height: 16)
                                .background(bus.isMuted ? Color.orange : Color.gray.opacity(0.2))
                                .foregroundColor(.white)
                                .cornerRadius(2)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("BusMuteButton_\(bus.id)")
                        
                        Button(action: { soundManager.toggleSolo(onBus: bus.id) }) {
                            Text("S")
                                .font(.system(size: 8, weight: .bold))
                                .frame(width: 16, height: 16)
                                .background(bus.isSolo ? Color.green : Color.gray.opacity(0.2))
                                .foregroundColor(.white)
                                .cornerRadius(2)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("BusSoloButton_\(bus.id)")

                        
                        // Output Route Picker
                        Menu {
                            ForEach(soundManager.availableOutputs, id: \.self) { outputName in
                                Button(outputName) {
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
                        .accessibilityIdentifier("RoutingMenu_\(bus.id)")
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
            .contextMenu {
                // Rename option
                Button(action: {
                    editedName = bus.name
                    isEditingName = true
                }) {
                    Label("Rename Bus", systemImage: "pencil")
                }
                
                Divider()
                
                // Color palette submenu
                Menu("Set Color") {
                    ForEach(colorPalette, id: \.hex) { color in
                        Button(action: {
                            soundManager.setBusColor(color.hex, onBus: bus.id)
                        }) {
                            HStack {
                                Circle()
                                    .fill(Color(hex: color.hex))
                                    .frame(width: 12, height: 12)
                                Text(color.name)
                            }
                        }
                    }
                }
            }
            
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
                _ = providers.first?.loadObject(ofClass: String.self) { (str, error) in
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
        .accessibilityIdentifier("BusTrack_\(bus.id)")
    }
}
