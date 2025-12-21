import SwiftUI

struct WebSocketInspectorView: View {
    @Binding var isVisible: Bool
    @State private var wsUrl: String = Config.websocketUrl
    @State private var isConnected: Bool = false
    
    var body: some View {
        if isVisible {
            HStack(spacing: 0) {
                Divider()
                
                VStack(alignment: .leading, spacing: 16) {
                    
                    // Header
                    HStack {
                        Text("NETWORK CONFIG")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.secondary)
                        Spacer()
                        Button(action: { isVisible = false }) {
                            Image(systemName: "xmark")
                                .font(.system(size: 10))
                        }
                        .buttonStyle(.plain)
                    }
                    
                    // URL Config
                    VStack(alignment: .leading, spacing: 4) {
                        Text("WebSocket URL")
                            .font(.system(size: 10))
                        TextField("ws://...", text: $wsUrl)
                            .textFieldStyle(.roundedBorder)
                            .font(.system(size: 11))
                    }
                    
                    // Connection Status
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Circle()
                                .fill(isConnected ? Color.green : Color.red)
                                .frame(width: 8, height: 8)
                            Text(isConnected ? "CONNECTED" : "DISCONNECTED")
                                .font(.system(size: 10, weight: .bold))
                                .foregroundColor(isConnected ? .green : .red)
                        }
                        
                        Button(action: { isConnected.toggle() }) {
                            Text(isConnected ? "DISCONNECT" : "CONNECT")
                                .font(.system(size: 10, weight: .bold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 4)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(isConnected ? .red : .blue)
                    }
                    
                    Divider()
                    
                    // Mini Log
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Recent Logs")
                            .font(.system(size: 10, weight: .bold))
                            .foregroundColor(.secondary)
                        
                        ScrollView {
                            VStack(alignment: .leading, spacing: 2) {
                                Text("[12:00:01] System Init")
                                Text("[12:00:02] Audio Engine Ready")
                                Text("[12:00:05] Waiting for connection...")
                            }
                            .font(.system(size: 9, design: .monospaced))
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .frame(height: 100)
                        .background(Color(nsColor: .controlBackgroundColor))
                        .cornerRadius(4)
                    }
                    
                    Spacer()
                }
                .padding()
                .frame(width: 250)
                .background(Color(nsColor: .windowBackgroundColor))
            }
            .transition(.move(edge: .trailing))
        }
    }
}
