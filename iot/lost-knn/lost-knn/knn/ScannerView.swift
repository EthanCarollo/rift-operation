import SwiftUI
import Combine

struct ScannerView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var knnService: KNNService
    
    // Throttler - User requested 500ms (0.5s)
    let timer = Timer.publish(every: 0.5, on: .main, in: .common).autoconnect()
    
    // State to track if view is active
    @State private var isVisible = false
    
    var body: some View {
        ZStack {
            // Full Screen Camera
            CameraPreview(cameraManager: cameraManager)
                .ignoresSafeArea()
            
            // Modern HUD Overlay
            VStack {
                Spacer()
                
                // Result Card
                VStack(spacing: 8) {
                    Text("DETECTED OBJECT")
                        .font(.custom("AvenirNext-Medium", size: 12))
                        .tracking(1.5)
                        .foregroundColor(.white.opacity(0.8))
                    
                    Text(knnService.predictedLabel)
                        .font(.custom("AvenirNext-Bold", size: 38))
                        .foregroundColor(.white)
                        .shadow(radius: 5)
                        .multilineTextAlignment(.center)
                        
                    // Visual indicator
                    HStack(spacing: 4) {
                        Circle().fill(isVisible ? Color.green : Color.gray).frame(width: 8, height: 8)
                        Text(isVisible ? "Scanning" : "Paused")
                            .font(.caption2)
                            .foregroundColor(isVisible ? .green : .gray)
                    }
                    .padding(.top, 4)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 30)
                .background(.ultraThinMaterial) // Glassmorphism
                .cornerRadius(30)
                .padding(20)
                .padding(.bottom, 50) // Tab bar clearance
            }
        }
        .onAppear { isVisible = true }
        .onDisappear { isVisible = false }
        .onReceive(timer) { _ in
            guard isVisible else { return } // Only run if tab is active
            
            if let frame = cameraManager.getLatestFrame() {
                knnService.predict(buffer: frame)
            }
        }
    }
}
