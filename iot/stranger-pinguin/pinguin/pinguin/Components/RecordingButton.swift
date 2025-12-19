import SwiftUI

struct RecordingButton: View {
    let isRecording: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            ZStack {
                Circle()
                    .stroke(Color.black.opacity(0.2), lineWidth: 1)
                    .frame(width: 80, height: 80)
                
                Circle()
                    .fill(isRecording ? Color.red : Color.black)
                    .frame(width: 60, height: 60)
                
                if isRecording {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.white)
                        .frame(width: 24, height: 24)
                } else {
                    Circle()
                        .fill(Color.white)
                        .frame(width: 20, height: 20)
                }
            }
        }
        .padding(.bottom, 40)
    }
}
