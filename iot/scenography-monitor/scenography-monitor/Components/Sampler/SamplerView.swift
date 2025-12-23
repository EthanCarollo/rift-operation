
import SwiftUI

struct SamplerView: View {
    @StateObject private var soundManager = SoundManager.shared
    
    // Layout State
    @State private var libraryWidth: CGFloat = 250
    
    var body: some View {
        HSplitView {
            // LEFT: Resource Library
            // We reuse SoundLibraryView but maybe we can customize it to be "Compact" if needed.
            // For now, it works as is.
            SoundLibraryView()
                .frame(minWidth: 200, maxWidth: 400)
                .layoutPriority(1)
            
            // RIGHT: Track Rack
            VStack(spacing: 0) {
                // Toolbar Area (Global controls could go here)
                HStack {
                    Text("PROJECT RACK")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(.secondary)
                    Spacer()
                }
                .padding(8)
                .background(Color(nsColor: .windowBackgroundColor))
                .border(Color(nsColor: .separatorColor), width: 1, edges: [.bottom])
                
                // Tracks ScrollView
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: 1) { // 1px spacing for simple separator look
                        ForEach(soundManager.audioBuses) { bus in
                            BusTrackView(bus: bus, soundManager: soundManager)
                        }
                    }
                    .padding(.bottom, 50)
                }
                .background(Color(nsColor: .controlBackgroundColor))
            }
            .frame(minWidth: 400, maxWidth: .infinity)
        }
    }
}
