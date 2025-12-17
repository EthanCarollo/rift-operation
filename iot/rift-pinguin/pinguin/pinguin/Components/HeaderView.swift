import SwiftUI

struct HeaderView: View {
    var body: some View {
        Text("RIFT OPERATION")
            .font(.system(size: 14, weight: .medium, design: .monospaced))
            .tracking(2)
            .foregroundStyle(.white.opacity(0.8))
            .padding(.top, 40)
    }
}
