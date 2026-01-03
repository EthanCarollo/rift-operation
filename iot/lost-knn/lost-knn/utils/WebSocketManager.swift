//
//  WebSocketManager.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025.
//

import SwiftUI
import Combine
import Starscream

class WebSocketManager: ObservableObject, WebSocketDelegate {
    @Published var isConnected = false
    @Published var isScanningEnabled = false
    @Published var messages: [String] = []
    
    // Starscream WebSocket
    private var socket: WebSocket?
    private let serverUrl = URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
    
    // State Management
    private var lastState: [String: Any] = [:]
    
    init() {
        // Init logic if needed
    }

    func sendDrawingRecognized(_ status: Bool) {
        guard isConnected else { return }
        
        var payload = self.lastState
        payload["lost_drawing_recognized"] = status
        payload["device_id"] = "lost-flower-phone"
        
        do {
            let data = try JSONSerialization.data(withJSONObject: payload, options: [])
            if let string = String(data: data, encoding: .utf8) {
                print("[WebSocket] Sending Drawing Recognized (\(status)): \(string)")
                self.sendMessage(string)
            }
        } catch {
            print("Failed to encode drawing recognized payload: \(error)")
        }
    }
    
    func connect() {
        var request = URLRequest(url: serverUrl)
        request.timeoutInterval = 5
        // Starscream setup
        socket = WebSocket(request: request)
        socket?.delegate = self
        socket?.connect()
        
        appendMessage("Connecting to \(serverUrl.absoluteString)...")
    }
    
    func disconnect() {
        socket?.disconnect()
        self.isConnected = false
        appendMessage("Disconnected.")
    }
    
    func sendMessage(_ text: String) {
        socket?.write(string: text)
    }
    
    // MARK: - Starscream Delegate Methods
    
    func didReceive(event: WebSocketEvent, client: WebSocketClient) {
        // Dispatch all UI updates to main thread
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            switch event {
            case .connected(let headers):
                self.isConnected = true
                self.appendMessage("Connected! Headers: \(headers)")
                
            case .disconnected(let reason, let code):
                self.isConnected = false
                self.appendMessage("Disconnected: \(reason) with code: \(code)")
                
            case .text(let string):
                self.appendMessage("Received: \(string)")
                // Parse for Sound Commands
                if let data = string.data(using: .utf8) {
                    do {
                        if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                            // 1. Store State
                            self.lastState = json
                            // 2. Check for lost_mp3_play
                            if let filename = json["lost_mp3_play"] as? String, !filename.isEmpty {
                                print("[WebSocket] Triggering Sound: \(filename)")
                                NotificationCenter.default.post(name: Notification.Name("PlaySoundNotification"), object: nil, userInfo: ["filename": filename])
                                self.appendMessage("Executing: lost_mp3_play -> \(filename)")
                                // Logic Trigger: Start Scanning on specific intro sound
                                if filename == "welcome_intro.mp3" {
                                    self.isScanningEnabled = true
                                    self.appendMessage("LOGIC: Scanning Enabled via intro")
                                }
                            }
                        }
                    } catch {
                        // Not JSON - Ignore
                    }
                }
                
            case .binary(let data):
                self.appendMessage("Received data: \(data.count) bytes")
                
            case .ping(_):
                break
                
            case .pong(_):
                break
                
            case .viabilityChanged(_):
                break
                
            case .reconnectSuggested(_):
                break
                
            case .cancelled:
                self.isConnected = false
                self.appendMessage("Connection Cancelled")
                
            case .error(let error):
                self.isConnected = false
                if let e = error {
                    self.appendMessage("Error: \(e.localizedDescription)")
                    // ATS Error handling hint
                    if e.localizedDescription.contains("Transport Security") {
                         self.appendMessage("HINT: Add 'Allow Arbitrary Loads' to Info.plist!")
                    }
                } else {
                    self.appendMessage("Unknown Error")
                }
                
            case .peerClosed:
                self.isConnected = false
                self.appendMessage("Peer Closed Connection")
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
