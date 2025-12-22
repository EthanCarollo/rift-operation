import Foundation
import Combine

class WebSocketManager: ObservableObject {
    static let shared = WebSocketManager()
    
    @Published var isConnected: Bool = false
    @Published var messages: [String] = [] // Log history
    
    // Store latest full JSON for anyone interested
    @Published var latestData: [String: Any] = [:]
    
    private var webSocketTask: URLSessionWebSocketTask?
    private var reconnectTimer: Timer?
    private let urlString = Config.websocketUrl
    
    private init() {
        connect()
    }
    
    func connect() {
        guard let url = URL(string: urlString) else { return }
        
        // Debug
        addLog("Connecting to \(urlString)...")
        
        let session = URLSession(configuration: .default)
        webSocketTask = session.webSocketTask(with: url)
        webSocketTask?.resume()
        
        self.isConnected = true // Tentative, or wait for open event?
                                // URLSessionWebSocketTask doesn't have a clear "opened" delegate easily without using a delegate class.
                                // We'll assume connected until error.
        
        receiveMessage()
    }
    
    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        DispatchQueue.main.async {
            self.isConnected = false
            self.addLog("Disconnected")
        }
    }
    
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }
            
            switch result {
            case .failure(let error):
                DispatchQueue.main.async {
                    self.isConnected = false
                    self.addLog("Error: \(error.localizedDescription)")
                    self.scheduleReconnect()
                }
            case .success(let message):
                switch message {
                case .string(let text):
                    self.handleMessage(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self.handleMessage(text)
                    }
                @unknown default:
                    break
                }
                
                // Continue listening
                self.receiveMessage()
            }
        }
    }
    
    private func handleMessage(_ text: String) {
        // Log generic
        // check if it's the big JSON
        DispatchQueue.main.async {
            self.addLog("RX: \(text.prefix(200))...")
            
            // Try parse
            if let data = text.data(using: .utf8) {
                do {
                    if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                        self.latestData = json
                        // Notify triggers? handled by Combine subscription to latestData
                    }
                } catch {
                     self.addLog("JSON Parse Error")
                }
            }
        }
    }
    
    private func scheduleReconnect() {
        // Simple backoff
        if reconnectTimer == nil {
            reconnectTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: false) { [weak self] _ in
                self?.reconnectTimer = nil
                self?.connect()
            }
        }
    }
    
    private func addLog(_ msg: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let entry = "[\(timestamp)] \(msg)"
        if messages.count > 50 { messages.removeFirst() }
        messages.append(entry)
    }
}
