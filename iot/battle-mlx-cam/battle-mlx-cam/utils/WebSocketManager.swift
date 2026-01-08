//
//  WebSocketManager.swift
//  battle-mlx-cam
//
//  WebSocket manager using Starscream
//

import SwiftUI
import Combine
import Starscream

class WebSocketManager: ObservableObject, WebSocketDelegate {
    @Published var isConnected = false
    @Published var messages: [String] = []
    @Published var battleState: String = "idle"
    
    private var socket: WebSocket?
    private let serverUrl = URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
    private var lastState: [String: Any] = [:]
    
    init() {}
    
    func connect() {
        var request = URLRequest(url: serverUrl)
        request.timeoutInterval = 5
        socket = WebSocket(request: request)
        socket?.delegate = self
        socket?.connect()
        appendMessage("Connecting to \(serverUrl.absoluteString)...")
    }
    
    func disconnect() {
        socket?.disconnect()
        isConnected = false
        appendMessage("Disconnected.")
    }
    
    func sendDrawingRecognised(dream: Bool?, nightmare: Bool?) {
        guard isConnected else { return }
        
        var payload = lastState
        payload["device_id"] = "battle-camera-mac"
        
        if let dream = dream {
            payload["battle_drawing_dream_recognised"] = dream
        }
        if let nightmare = nightmare {
            payload["battle_drawing_nightmare_recognised"] = nightmare
        }
        
        sendPayload(payload)
    }
    
    func sendHitConfirmed(_ confirmed: Bool) {
        guard isConnected else { return }
        
        var payload = lastState
        payload["device_id"] = "battle-camera-mac"
        payload["battle_hit_confirmed"] = confirmed
        
        sendPayload(payload)
    }
    
    private func sendPayload(_ payload: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: payload),
              let string = String(data: data, encoding: .utf8) else {
            return
        }
        
        appendMessage("Sending: \(Array(payload.keys).filter { $0.hasPrefix("battle_") })")
        socket?.write(string: string)
        lastState = payload
    }
    
    // MARK: - Starscream Delegate
    
    func didReceive(event: WebSocketEvent, client: WebSocketClient) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            switch event {
            case .connected(let headers):
                self.isConnected = true
                self.appendMessage("Connected! Headers: \(headers)")
                
            case .disconnected(let reason, let code):
                self.isConnected = false
                self.appendMessage("Disconnected: \(reason) code: \(code)")
                
            case .text(let string):
                self.handleMessage(string)
                
            case .binary(let data):
                self.appendMessage("Received binary: \(data.count) bytes")
                
            case .ping(_), .pong(_), .viabilityChanged(_), .reconnectSuggested(_):
                break
                
            case .cancelled:
                self.isConnected = false
                self.appendMessage("Connection Cancelled")
                
            case .error(let error):
                self.isConnected = false
                if let e = error {
                    self.appendMessage("Error: \(e.localizedDescription)")
                }
                
            case .peerClosed:
                self.isConnected = false
                self.appendMessage("Peer Closed")
            }
        }
    }
    
    private func handleMessage(_ text: String) {
        appendMessage("Received: \(text.prefix(100))...")
        
        guard let data = text.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return
        }
        
        lastState = json
        
        if let state = json["battle_state"] as? String {
            battleState = state
        }
    }
    
    private func appendMessage(_ text: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        messages.insert("[\(timestamp)] \(text)", at: 0)
        if messages.count > 50 {
            messages.removeLast()
        }
    }
}
