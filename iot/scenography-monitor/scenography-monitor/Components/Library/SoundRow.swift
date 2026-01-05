
import SwiftUI
import AppKit

struct SoundRow: View {
    let node: SoundManager.FileNode
    @State private var isRenaming = false
    @State private var newName: String = ""
    
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
        .contextMenu {
            Button("Rename") {
                newName = node.name
                isRenaming = true
            }
            Button("Show in Finder") {
                NSWorkspace.shared.activateFileViewerSelecting([node.url])
            }
        }
        .popover(isPresented: $isRenaming) {
            VStack(spacing: 8) {
                Text("Rename Sound")
                    .font(.headline)
                TextField("New Name", text: $newName)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 200)
                    .onSubmit {
                        performRename()
                    }
                HStack {
                    Button("Cancel") { isRenaming = false }
                    Button("Rename") { performRename() }
                        .keyboardShortcut(.defaultAction)
                }
            }
            .padding()
        }
    }
    
    private func performRename() {
        SoundManager.shared.renameSound(at: node.url, to: newName)
        isRenaming = false
    }
}
