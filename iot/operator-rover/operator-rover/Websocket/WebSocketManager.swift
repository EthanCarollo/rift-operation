//
//  WebsocketManager.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

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
        case .prod: return URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
        // case .dev:  return URL(string: "ws://192.168.10.7:8000/ws")! // User asked for specific dev IP
        // Wait, user said: "dev : ws://server.riftoperation.ethan-folio.fr/ws', prod :ws://192.168.10.7:8000/ws"
        // Actually typically 192.168... is Local/Dev and the eth-folio one is Prod.
        // User request: "dev : ws://server.riftoperation.ethan-folio.fr/ws', prod :ws://192.168.10.7:8000/ws"
        // That seems inverted but I will follow EXACT instructions.
        case .dev: return URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
        case .prod: return URL(string: "ws://192.168.10.7:8000/ws")!
        }
    }
}

extension Notification.Name {
    static let riftStepReceived = Notification.Name("riftStepReceived")
}

final class WebSocketManager: ObservableObject, WebSocketDelegate {
    
    // MARK: - Published State
    @Published var isConnected: Bool = false
    @Published var logs: [LogMessage] = []
    @Published var serverMode: ServerMode = .dev {
        didSet {
            // Reconnect on change
            disconnect()
            setupSocket()
        }
    }
    
    // MARK: - Private
    private var socket: WebSocket?
    
    init() {
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
        guard !isConnected else { return }
        log("Attempting to connect to \(serverMode.url.absoluteString)...")
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
            handleMessage(string)
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

    private func handleMessage(_ text: String) {
        // Parse JSON
        guard let data = text.data(using: .utf8) else { return }
        do {
            if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                // Check payload wrapper if needed, assume flat or 'value' wrapper
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

