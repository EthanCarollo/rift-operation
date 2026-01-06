import Foundation
import Combine

class WebSocketManager: ObservableObject {
    static let shared = WebSocketManager()
    
    private static let urlDefaultsKey = "websocketUrl"
    
    @Published var isConnected: Bool = false
    @Published var messages: [String] = [] // Log history
    
    // Store latest full JSON for anyone interested
    @Published var latestData: [String: Any] = [:]
    
    // Editable URL - persisted in UserDefaults
    @Published var urlString: String {
        didSet {
            UserDefaults.standard.set(urlString, forKey: WebSocketManager.urlDefaultsKey)
        }
    }
    
    private var webSocketTask: URLSessionWebSocketTask?
    private var reconnectTimer: Timer?
    
    private init() {
        // Load saved URL or use default
        self.urlString = UserDefaults.standard.string(forKey: WebSocketManager.urlDefaultsKey) ?? Config.defaultWebsocketUrl
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
    
    func handleMessage(_ text: String) {
        // Offload parsing to background thread to clear Main Thread
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            var parsedJson: [String: Any]? = nil
            var parseError = false
            
            if let data = text.data(using: .utf8) {
                do {
                    parsedJson = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]
                } catch {
                    parseError = true
                }
            }
            
            // Update UI/State on Main Thread
            DispatchQueue.main.async {
                self.addLog("RX: \(text.prefix(200))...")
                
                if let json = parsedJson {
                    self.latestData = json
                } else if parseError {
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
    
    func addLog(_ msg: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        let entry = "[\(timestamp)] \(msg)"
        if messages.count > 50 { messages.removeFirst() }
        messages.append(entry)
    }
}
