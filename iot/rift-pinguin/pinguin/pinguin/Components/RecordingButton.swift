import SwiftUI

struct RecordingButton: View {
    let isRecording: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            ZStack {
                Circle()
                    .stroke(Color.white.opacity(0.2), lineWidth: 1)
                    .frame(width: 80, height: 80)
                
                Circle()
                    .fill(isRecording ? Color.red : Color.white)
                    .frame(width: 60, height: 60)
                    .overlay(
                        Circle()
                            .stroke(Color.black, lineWidth: 2)
                            .opacity(isRecording ? 0 : 1)
                    )
                
                if isRecording {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.white)
                        .frame(width: 24, height: 24)
                }
            }
        }
        .padding(.bottom, 40)
    }
}
