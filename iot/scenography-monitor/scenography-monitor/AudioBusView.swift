import SwiftUI

struct AudioBusView: View {
    let busName: String
    let busId: Int
    @State private var volume: Double = 0.75
    @State private var pan: Double = 0.5
    @State private var isMuted: Bool = false
    @State private var isSolo: Bool = false
    @State private var selectedDevice: String = ""
    
    // Mock devices
    let devices = ["Built-in Output", "Scarlett 2i2", "Virtual Cable 1", "HDMI Audio"]
    
    var body: some View {
        VStack(spacing: 0) {
            // Bus Header
            Text(busName)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(.primary)
                .frame(height: 30)
                .frame(maxWidth: .infinity)
                .background(Color(nsColor: .windowBackgroundColor))
                .border(Color(nsColor: .separatorColor), width: 0.5)
            
            // FX/Inserts Placeholder
            VStack(spacing: 1) {
                ForEach(0..<4) { _ in
                    Rectangle()
                        .fill(Color(nsColor: .controlBackgroundColor))
                        .frame(height: 16)
                        .overlay(
                            Rectangle()
                                .stroke(Color(nsColor: .separatorColor).opacity(0.3), lineWidth: 0.5)
                        )
                }
            }
            .padding(1)
            .background(Color(nsColor: .textBackgroundColor))
            
            Divider()
            
            // Controls Area
            VStack(spacing: 8) {
                
                // Pan Knob (Visual)
                ZStack {
                    Circle()
                        .stroke(Color.gray, lineWidth: 1)
                        .frame(width: 32, height: 32)
                    
                    Rectangle()
                        .fill(Color.gray)
                        .frame(width: 2, height: 10)
                        .offset(y: -8)
                        .rotationEffect(.degrees((pan * 270) - 135))
                        .gesture(DragGesture().onChanged { value in
                            // Simple horizontal drag to rotate
                            let sensitivity: Double = 0.01
                            pan = max(0, min(1, pan + (value.translation.width * sensitivity)))
                        })
                }
                .padding(.top, 8)
                
                // Fader & Meter Section
                HStack(alignment: .bottom, spacing: 4) {
                    
                    // Meter L
                    ZStack(alignment: .bottom) {
                        Rectangle()
                            .fill(Color.black.opacity(0.1))
                            .frame(width: 6, height: 160)
                        
                        // Gradient Fill (Static 0 for now as requested)
                        LinearGradient(
                            gradient: Gradient(colors: [.green, .yellow, .red]),
                            startPoint: .bottom,
                            endPoint: .top
                        )
                        .frame(width: 6, height: 0) // Height 0 for silence
                        .mask(Rectangle())
                    }
                    
                    // Fader Track
                    ZStack(alignment: .bottom) {
                        Rectangle()
                            .fill(Color(nsColor: .controlBackgroundColor))
                            .frame(width: 24, height: 160)
                            .overlay(
                                Rectangle() // Center line
                                    .fill(Color.black.opacity(0.1))
                                    .frame(width: 1)
                            )
                        
                        // Fader Handle
                        Rectangle()
                            .fill(Color(nsColor: .windowBackgroundColor))
                            .frame(width: 24, height: 32)
                            .overlay(
                                Rectangle()
                                    .fill(Color.black.opacity(0.5))
                                    .frame(height: 1)
                            )
                            .shadow(radius: 1, y: 1)
                            .offset(y: -((volume) * 128)) // 160 height - 32 handle = 128 travel
                            .gesture(DragGesture().onChanged { value in
                                // Invert drag because SwiftUI coordinates (0 at top) vs Offset (0 at bottom in this alignment context?)
                                // Actually simplified: just map drag to volume
                                let range: Double = 128
                                let sensitivity: Double = 0.005
                                volume = max(0, min(1, volume - (value.translation.height * sensitivity)))
                            })
                    }
                    
                    // Meter R
                    ZStack(alignment: .bottom) {
                        Rectangle()
                            .fill(Color.black.opacity(0.1))
                            .frame(width: 6, height: 160)
                        
                        LinearGradient(
                            gradient: Gradient(colors: [.green, .yellow, .red]),
                            startPoint: .bottom,
                            endPoint: .top
                        )
                        .frame(width: 6, height: 0)
                    }
                }
                
                // Mute/Solo
                HStack(spacing: 2) {
                    Button(action: { isMuted.toggle() }) {
                        Text("M")
                            .font(.system(size: 8, weight: .bold))
                            .frame(width: 16, height: 16)
                    }
                    .buttonStyle(.plain)
                    .background(isMuted ? Color.red : Color(nsColor: .controlBackgroundColor))
                    .foregroundColor(isMuted ? .white : .secondary)
                    .cornerRadius(2)
                    
                    Button(action: { isSolo.toggle() }) {
                        Text("S")
                            .font(.system(size: 8, weight: .bold))
                            .frame(width: 16, height: 16)
                    }
                    .buttonStyle(.plain)
                    .background(isSolo ? Color.yellow : Color(nsColor: .controlBackgroundColor))
                    .foregroundColor(isSolo ? .black : .secondary)
                    .cornerRadius(2)
                }
            }
            .padding(.bottom, 8)
            .frame(maxWidth: .infinity)
            .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
            
            Divider()
            
            // Output Picker
            VStack(spacing: 2) {
                Text("OUTPUT")
                    .font(.system(size: 8, weight: .bold))
                    .foregroundColor(.secondary)
                
                Picker("", selection: $selectedDevice) {
                    Text("-- Out --").tag("")
                    ForEach(devices, id: \.self) { device in
                        Text(device).tag(device)
                    }
                }
                .labelsHidden()
                .controlSize(.mini)
                .frame(maxWidth: 80)
            }
            .frame(height: 50)
            .frame(maxWidth: .infinity)
            .background(Color(nsColor: .windowBackgroundColor))
        }
        .frame(width: 90)
        .background(Color(nsColor: .windowBackgroundColor))
        .border(Color(nsColor: .separatorColor), width: 0.5)
    }
}

#Preview {
    AudioBusView(busName: "TEST", busId: 1)
}
