import SwiftUI

struct LogView: View {
    let text: String
    
    var body: some View {
        ScrollView {
            Text(text.isEmpty ? "Transcription will appear here..." : text)
                .font(.system(size: 24, weight: .light, design: .default))
                .foregroundStyle(.white)
                .multilineTextAlignment(.leading)
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .animation(.default, value: text)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.white.opacity(0.05))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(Color.white.opacity(0.1), lineWidth: 1)
        )
        .padding(.horizontal)
    }
}
