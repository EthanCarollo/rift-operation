import SwiftUI

struct WebSocketInspectorView: View {
    @Binding var isVisible: Bool
    
    @ObservedObject var wsManager = WebSocketManager.shared
    @ObservedObject var soundTrigger = SoundTrigger.shared
    
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
                    
                    // URL Editor
                    VStack(alignment: .leading, spacing: 4) {
                        Text("WebSocket URL")
                            .font(.system(size: 10, weight: .bold))
                            .foregroundColor(.secondary)
                        
                        HStack(spacing: 4) {
                            TextField("ws://...", text: $wsManager.urlString)
                                .textFieldStyle(.roundedBorder)
                                .font(.system(size: 11, design: .monospaced))
                                .accessibilityIdentifier("websocket_url_field")
                            
                            Button(action: {
                                wsManager.urlString = Config.defaultWebsocketUrl
                            }) {
                                Image(systemName: "arrow.counterclockwise")
                                    .font(.system(size: 10))
                            }
                            .buttonStyle(.borderless)
                            .help("Reset to default URL")
                            .accessibilityIdentifier("reset_url_button")
                        }
                    }
                    
                    // Connection Status
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Circle()
                                .fill(wsManager.isConnected ? Color.green : Color.red)
                                .frame(width: 8, height: 8)
                                .accessibilityIdentifier("connection_indicator")
                            Text(wsManager.isConnected ? "CONNECTED" : "DISCONNECTED")
                                .font(.system(size: 10, weight: .bold))
                                .foregroundColor(wsManager.isConnected ? .green : .red)
                                .accessibilityIdentifier("connection_status_label")
                        }
                        
                        Button(action: {
                            if wsManager.isConnected {
                                wsManager.disconnect()
                            } else {
                                wsManager.connect()
                            }
                        }) {
                            Text(wsManager.isConnected ? "DISCONNECT" : "CONNECT")
                                .font(.system(size: 10, weight: .bold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 4)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(wsManager.isConnected ? .red : .blue)
                        .accessibilityIdentifier("connect_button")
                    }
                    
                    Divider()
                    
                    Divider()
                    
                    // Mini Log
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Recent Logs")
                            .font(.system(size: 10, weight: .bold))
                            .foregroundColor(.secondary)
                        
                        ScrollView {
                            VStack(alignment: .leading, spacing: 2) {
                                ForEach(wsManager.messages.suffix(20).reversed(), id: \.self) { msg in
                                    Text(msg)
                                        .font(.system(size: 9, design: .monospaced))
                                        .foregroundColor(.secondary)
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .frame(maxHeight: .infinity)
                        .background(Color(nsColor: .controlBackgroundColor))
                        .cornerRadius(4)
                    }
                    
                    Spacer()
                }
                .padding()
                .frame(width: 300)
                .background(Color(nsColor: .windowBackgroundColor))
            }
            .transition(.move(edge: .trailing))
        }
    }
}
