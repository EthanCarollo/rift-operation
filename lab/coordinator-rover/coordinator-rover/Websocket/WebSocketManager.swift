import SwiftUI
import Combine
import Starscream

struct LogMessage: Identifiable, Hashable {
    let id = UUID()
    let text: String
}

final class WebSocketManager: ObservableObject, WebSocketDelegate {
    
    // MARK: - Published State
    @Published var isConnected: Bool = false
    @Published var logs: [LogMessage] = []
    
    // MARK: - Private
    private var socket: WebSocket?
    private let serverUrl = URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
    
    init() {
        setupSocket()
    }
    
    private func setupSocket() {
        var request = URLRequest(url: serverUrl)
        request.timeoutInterval = 5
        socket = WebSocket(request: request)
        socket?.delegate = self
        connect()
    }
    
    func connect() {
        guard !isConnected else { return }
        log("Attempting to connect to \(serverUrl.absoluteString)...")
        socket?.connect()
    }
    
    func disconnect() {
        socket?.disconnect()
    }
    
    // MARK: - WebSocketDelegate
    
    func didReceive(event: WebSocketEvent, client: WebSocketClient) {
        switch event {
        case .connected(let headers):
            DispatchQueue.main.async {
                self.isConnected = true
                self.log("Connected! Headers: \(headers)")
            }
        case .disconnected(let reason, let code):
            DispatchQueue.main.async {
                self.isConnected = false
                self.log("Disconnected: \(reason) with code: \(code)")
            }
        case .text(let string):
            DispatchQueue.main.async {
                self.log("Received text: \(string)")
            }
        case .binary(let data):
            DispatchQueue.main.async {
                self.log("Received data: \(data.count) bytes")
            }
        case .ping(_):
            break
        case .pong(_):
            break
        case .viabilityChanged(_):
            break
        case .reconnectSuggested(_):
            break
        case .cancelled:
            DispatchQueue.main.async {
                self.isConnected = false
                self.log("Cancelled")
            }
        case .error(let error):
            DispatchQueue.main.async {
                self.isConnected = false
                self.log("Error: \(error?.localizedDescription ?? "Unknown")")
                // Auto-reconnect after 5s
                DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
                    self.connect()
                }
            }
        case .peerClosed:
             DispatchQueue.main.async {
                self.isConnected = false
                self.log("Peer closed")
            }
        }
    }

    private func log(_ message: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let fullText = "[\(timestamp)] \(message)"
        let logMessage = LogMessage(text: fullText)
        
        DispatchQueue.main.async {
            self.logs.insert(logMessage, at: 0)
            if self.logs.count > 100 {
                self.logs.removeLast()
            }
        }
    }
}
