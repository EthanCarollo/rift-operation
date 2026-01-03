import SwiftUI

struct ContentView: View {
    @StateObject private var cameraManager = CameraManager()
    @StateObject private var KNNService = KNNServiceClass() // Renamed to avoid confusion if needed, assuming class name is KNNService
    
    init() {
        // Transparent TabBar
        let appearance = UITabBarAppearance()
        appearance.configureWithTransparentBackground()
        appearance.backgroundColor = UIColor.black.withAlphaComponent(0.5) // Semi-transparent
        
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
    }
    
    var body: some View {
        // LAYER 2: Application UI
        TabView {
            // Tab 1: Home
            VStack {
                Spacer()
                Image(systemName: "globe")
                    .imageScale(.large)
                    .foregroundStyle(.white)
                Text("Rift Lost KNN")
                    .font(.title)
                    .bold()
                    .foregroundColor(.white)
                    .shadow(radius: 5)
                Spacer()
            }
            .tabItem {
                Label("Home", systemImage: "house.fill")
            }
            
            // Tab 2: Scanner (Vision)
            ScannerView(cameraManager: cameraManager, knnService: KNNService)
                .tabItem {
                    Label("Scanner", systemImage: "eye.circle.fill")
                }
            
            // Tab 3: Training
            TrainingView(cameraManager: cameraManager, knnService: KNNService)
                .tabItem {
                    Label("Training", systemImage: "brain.head.profile")
                }
        }
        .accentColor(.yellow)
        .preferredColorScheme(.dark)
        .onAppear {
            cameraManager.start()
        }
    }
}

// Separate type alias to avoid conflict if any (Assuming KNNService is the class name)
typealias KNNServiceClass = KNNService
