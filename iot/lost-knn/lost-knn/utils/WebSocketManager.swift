//
//  WebSocketManager.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI
import Combine

class WebSocketManager: ObservableObject {
    @Published var isConnected = false
    @Published var messages: [String] = []
    
    private var webSocketTask: URLSessionWebSocketTask?
    private let url = URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
    
    func connect() {
        let session = URLSession(configuration: .default)
        webSocketTask = session.webSocketTask(with: url)
        webSocketTask?.resume()
        
        self.isConnected = true
        receiveMessage()
        
        print("[WebSocket] Connecting to \(url.absoluteString)")
        appendMessage("Connecting to server...")
    }
    
    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        self.isConnected = false
        appendMessage("Disconnected from server.")
    }
    
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }
            
            switch result {
            case .failure(let error):
                print("[WebSocket] Error: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self.isConnected = false
                    self.appendMessage("Error: \(error.localizedDescription)")
                }
            case .success(let message):
                switch message {
                case .string(let text):
                    DispatchQueue.main.async {
                        self.appendMessage("Received: \(text)")
                    }
                case .data(let data):
                    DispatchQueue.main.async {
                        self.appendMessage("Received data: \(data.count) bytes")
                    }
                @unknown default:
                    break
                }
                // Continue listening
                self.receiveMessage()
            }
        }
    }
    
    func sendMessage(_ text: String) {
        let message = URLSessionWebSocketTask.Message.string(text)
        webSocketTask?.send(message) { error in
            if let error = error {
                print("[WebSocket] Send error: \(error.localizedDescription)")
            }
        }
    }
    
    private func appendMessage(_ text: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        self.messages.insert("[\(timestamp)] \(text)", at: 0)
        // Keep log manageable
        if self.messages.count > 50 {
            self.messages.removeLast()
        }
    }
}
