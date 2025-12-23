
import SwiftUI

struct SoundRow: View {
    let node: SoundManager.FileNode
    
    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: "waveform")
                .font(.system(size: 10))
                .foregroundColor(.secondary)
            
            Text(node.name)
                .font(.system(size: 11, design: .monospaced))
                .lineLimit(1)
                .truncationMode(.middle)
                .foregroundColor(.primary)
            
            Spacer()
        }
        .padding(4)
        .contentShape(Rectangle())
        .onDrag {
            return NSItemProvider(object: node.name as NSString)
        }
    }
}
