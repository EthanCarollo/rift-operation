import SwiftUI

struct LogView: View {
    let text: String
    
    var body: some View {
        ScrollView {
            ScrollViewReader { proxy in
                Text(text.isEmpty ? "Transcription will appear here..." : text)
                    .font(.system(size: 36, weight: .regular, design: .default))
                    .foregroundStyle(.black)
                    .multilineTextAlignment(.leading)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .animation(.default, value: text)
                    .id("bottom")
                    .onChange(of: text) { _ in
                        withAnimation {
                            proxy.scrollTo("bottom", anchor: .bottom)
                        }
                    }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.03))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 20)
                .stroke(Color.black.opacity(0.1), lineWidth: 1)
        )
        .padding(.horizontal)
    }
}
