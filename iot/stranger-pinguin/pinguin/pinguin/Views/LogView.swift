import SwiftUI

struct LogView: View {
    let text: String
    
    var body: some View {
        ScrollView {
            ScrollViewReader { proxy in
                VStack(alignment: .leading, spacing: 0) {
                    Text(text.isEmpty ? "L'écoute commence ici..." : text)
                        .font(.system(size: 32, weight: .light, design: .serif))
                        .foregroundStyle(.black.opacity(0.8))
                        .multilineTextAlignment(.leading)
                        .lineSpacing(8)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    // Hidden anchor at the very bottom
                    Spacer()
                        .frame(height: 1)
                        .id("bottom_anchor")
                }
                .onChange(of: text) { _ in
                    withAnimation(.easeOut(duration: 0.3)) {
                        proxy.scrollTo("bottom_anchor", anchor: .bottom)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 24)
                .fill(Color.black.opacity(0.02))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 24)
                .stroke(Color.black.opacity(0.05), lineWidth: 1)
        )
        .padding(.horizontal)
    }
}
