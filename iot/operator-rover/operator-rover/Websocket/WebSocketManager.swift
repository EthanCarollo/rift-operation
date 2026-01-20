
import SwiftUI
import Combine
import Starscream

struct LogMessage: Identifiable, Hashable {
    let id = UUID()
    let text: String
}

enum ServerMode: String, CaseIterable, Identifiable {
    case prod = "Production"
    case dev = "Development"
    var id: String { self.rawValue }
    
    var url: URL {
        switch self {
        case .dev: return URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
        case .prod: return URL(string: "ws://192.168.10.7:8000/ws")!
        }
    }
}

extension Notification.Name {
    static let riftStepReceived = Notification.Name("riftStepReceived")
}

enum ConnectionStatus: String {
    case disconnected = "DISCONNECTED"
    case connecting = "CONNECTING..."
    case connected = "CONNECTED"
}

final class WebSocketManager: ObservableObject, WebSocketDelegate {
    
    // MARK: - Published State
    @Published var connectionStatus: ConnectionStatus = .disconnected
    @Published var logs: [LogMessage] = []
    
    @Published var serverMode: ServerMode = .dev {
        didSet {
            // Avoid "Publishing changes from within view updates" error
            // by dispatching the side-effect asynchronously
            guard oldValue != serverMode else { return }
            log("Switching to \(serverMode.rawValue)...")
            DispatchQueue.main.async {
                self.respawnSocket()
            }
        }
    }
    
    // MARK: - Private
    private var socket: WebSocket?
    private var timer: Timer?
    
    init() {
        respawnSocket()
    }
    
    private func respawnSocket() {
        disconnect()
        setupSocket()
    }
    
    private func setupSocket() {
        var request = URLRequest(url: serverMode.url)
        request.timeoutInterval = 5
        socket = WebSocket(request: request)
        socket?.delegate = self
        connect()
    }
    
    func connect() {
        guard connectionStatus != .connected else { return }
        updateStatus(.connecting)
        log("Attempting to connect to \(serverMode.url.absoluteString)...")
        socket?.connect()
    }
    
    func disconnect() {
        socket?.disconnect()
        // We don't set status here immediately, we wait for callback
        // or force it if socket is nil
    }
    
    private func updateStatus(_ status: ConnectionStatus) {
        // Ensure UI updates are on main thread
        DispatchQueue.main.async {
            self.connectionStatus = status
        }
    }
    
    // MARK: - WebSocketDelegate
    
    func didReceive(event: WebSocketEvent, client: WebSocketClient) {
        switch event {
        case .connected(let headers):
            updateStatus(.connected)
            DispatchQueue.main.async { self.log("Connected! Headers: \(headers)") }
            
        case .disconnected(let reason, let code):
            updateStatus(.disconnected)
            DispatchQueue.main.async { self.log("Disconnected: \(reason) with code: \(code)") }
            
        case .text(let string):
            handleMessage(string)
            DispatchQueue.main.async { self.log("Received: \(string)") }
            
        case .binary(let data):
            DispatchQueue.main.async { self.log("Received data: \(data.count) bytes") }
            
        case .ping(_): break
        case .pong(_): break
        case .viabilityChanged(_): break
        case .reconnectSuggested(_): break
            
        case .cancelled:
            updateStatus(.disconnected)
            DispatchQueue.main.async { self.log("Cancelled") }
            
        case .error(let error):
            updateStatus(.disconnected)
            DispatchQueue.main.async {
                self.log("Error: \(error?.localizedDescription ?? "Unknown")")
                // Auto-reconnect
                self.scheduleReconnect()
            }
            
        case .peerClosed:
             updateStatus(.disconnected)
             DispatchQueue.main.async { self.log("Peer closed") }
        }
    }
    
    private func scheduleReconnect() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 5) { [weak self] in
            // Only reconnect if we are still disconnected
            guard let self = self, self.connectionStatus == .disconnected else { return }
            self.log("Auto-reconnecting...")
            self.connect()
        }
    }

    private func handleMessage(_ text: String) {
        guard let data = text.data(using: .utf8) else { return }
        do {
            if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                let payload = (json["value"] as? [String: Any]) ?? json
                
                let s1 = payload["operator_launch_close_rift_step_1"] as? Bool ?? false
                let s2 = payload["operator_launch_close_rift_step_2"] as? Bool ?? false
                let s3 = payload["operator_launch_close_rift_step_3"] as? Bool ?? false
                
                if s1 || s2 || s3 {
                    DispatchQueue.main.async {
                        NotificationCenter.default.post(name: .riftStepReceived, object: nil)
                        self.log("Rift Step Detected -> Triggering Rover")
                    }
                }
            }
        } catch {
            print("JSON Parse Error: \(error)")
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
