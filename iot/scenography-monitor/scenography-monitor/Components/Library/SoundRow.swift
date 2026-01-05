
import SwiftUI
import AppKit
import AVFoundation

struct SoundRow: View {
    let node: SoundManager.FileNode
    @State private var isRenaming = false
    @State private var newName: String = ""
    @ObservedObject var soundManager = SoundManager.shared
    
    var isSelected: Bool {
        soundManager.selectedSoundURL == node.url
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Filename Row
            HStack(spacing: 6) {
                Image(systemName: "waveform")
                    .font(.system(size: 10))
                    .foregroundColor(isSelected ? .white : .secondary)
                
                Text(node.name)
                    .font(.system(size: 11, design: .monospaced))
                    .lineLimit(1)
                    .truncationMode(.middle)
                    .foregroundColor(isSelected ? .white : .primary)
                
                Spacer()
            }
            
            // Mini Waveform + Duration
            HStack(spacing: 4) {
                WaveformView(url: node.url, tintColor: isSelected ? .white.opacity(0.9) : .blue.opacity(0.6))
                    .frame(height: 20)
                
                // Duration
                Text(formatDuration(for: node.url))
                    .font(.system(size: 9, design: .monospaced))
                    .foregroundColor(isSelected ? .white.opacity(0.7) : .secondary)
            }
        }
        .padding(.horizontal, 6)
        .padding(.vertical, 6)
        .frame(minWidth: 180)
        .background(isSelected ? Color.blue : Color.clear)
        .cornerRadius(6)
        .contentShape(Rectangle())
        .onTapGesture {
            soundManager.selectedSoundURL = node.url
        }
        .onDrag {
            return NSItemProvider(object: node.name as NSString)
        }
        .contextMenu {
            Button("Play Preview") {
                playPreview()
            }
            Divider()
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
    
    private func formatDuration(for url: URL) -> String {
        do {
            let file = try AVAudioFile(forReading: url)
            let duration = Double(file.length) / file.processingFormat.sampleRate
            let minutes = Int(duration) / 60
            let seconds = Int(duration) % 60
            return String(format: "%d:%02d", minutes, seconds)
        } catch {
            return "--:--"
        }
    }
    
    private func playPreview() {
        // Quick preview on default output
        SoundManager.shared.previewSound(at: node.url)
    }
}

