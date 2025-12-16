//
//  WebsocketView.swift
//  IOTTools
//
//  Created by Tom Boullay on 15/12/2025
//

import SwiftUI
import Combine
import Foundation

// MARK: - WebSocket client Rift
final class RiftWebSocketClient: ObservableObject {

    // Config de base pour ton serveur Rift
    struct Config {
        let url = URL(string: "ws://server.riftoperation.ethan-folio.fr/ws")!
        let deviceId = "sphero-forest-ios-01"
        let workshop = "forest"
        let role = "sphero"
    }

    // Messages envoyés au serveur

    struct HelloMessage: Codable {
        struct Value: Codable {
            let deviceId: String
            let workshop: String
            let role: String
        }

        let type: String = "hello"
        let value: Value
    }

    struct TelemetryMessage: Codable {
        struct Value: Codable {
            let deviceId: String
            let workshop: String
            let tsMs: Int
            let room: String
            let event: String
        }

        let type: String = "telemetry"
        let value: Value
    }

    // MARK: - Public API observable

    @Published var isConnected: Bool = false
    @Published var logLines: [String] = []
    @Published var lastError: String?

    private let config = Config()
    private var task: URLSessionWebSocketTask?

    // MARK: - Connection

    func connect() {
        guard task == nil else { return } // déjà connecté/en cours

        appendLog("🔌 Connecting to \(config.url.absoluteString)...")

        let task = URLSession.shared.webSocketTask(with: config.url)
        self.task = task

        task.resume()
        isConnected = true

        // Dès qu'on est up, on écoute & on envoie le hello
        listen()
        sendHello()
    }

    func disconnect() {
        guard let task else { return }

        appendLog("🔌 Disconnect requested")
        task.cancel(with: .goingAway, reason: nil)
        self.task = nil
        isConnected = false
    }

    // MARK: - Send messages

    private func sendHello() {
        let msg = HelloMessage(
            value: .init(
                deviceId: config.deviceId,
                workshop: config.workshop,
                role: config.role
            )
        )

        sendCodable(msg, label: "HELLO")
    }

    /// Petit bouton de test pour envoyer une télémétrie fake
    func sendTestTelemetry() {
        let ts = Int(Date().timeIntervalSince1970 * 1000)

        let msg = TelemetryMessage(
            value: .init(
                deviceId: config.deviceId,
                workshop: config.workshop,
                tsMs: ts,
                room: "child",
                event: "sphero_test_ping"
            )
        )

        sendCodable(msg, label: "TELEMETRY")
    }

    private func sendCodable<T: Codable>(_ value: T, label: String) {
        guard let task else {
            appendLog("⚠️ Cannot send \(label): not connected")
            return
        }

        do {
            let data = try JSONEncoder().encode(value)
            guard let json = String(data: data, encoding: .utf8) else {
                appendLog("⚠️ Encode error for \(label): invalid UTF-8")
                return
            }

            appendLog(">> \(label): \(json)")
            task.send(.string(json)) { [weak self] error in
                if let error {
                    DispatchQueue.main.async {
                        self?.appendLog("❌ Send error: \(error.localizedDescription)")
                        self?.lastError = error.localizedDescription
                    }
                }
            }
        } catch {
            appendLog("❌ JSON encode error: \(error)")
            lastError = error.localizedDescription
        }
    }

    // MARK: - Receive loop

    private func listen() {
        guard let task else { return }

        task.receive { [weak self] result in
            guard let self else { return }

            switch result {
            case .failure(let error):
                DispatchQueue.main.async {
                    self.appendLog("❌ Receive error: \(error.localizedDescription)")
                    self.lastError = error.localizedDescription
                    self.isConnected = false
                    self.task = nil
                }

            case .success(let message):
                DispatchQueue.main.async {
                    switch message {
                    case .string(let text):
                        self.appendLog("<< \(text)")
                    case .data(let data):
                        let size = data.count
                        self.appendLog("<< [binary data \(size) bytes]")
                    @unknown default:
                        self.appendLog("<< [unknown message]")
                    }
                }

                // On continue à écouter tant que la connexion est vivante
                self.listen()
            }
        }
    }

    // MARK: - Logging util

    private func appendLog(_ line: String) {
        print("[WS] \(line)")
        logLines.append(line)

        // garde un log raisonnable
        if logLines.count > 200 {
            logLines.removeFirst(logLines.count - 200)
        }
    }
}

// MARK: - SwiftUI View

struct WebsocketView: View {

    @StateObject private var client = RiftWebSocketClient()

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {

            // Status
            HStack(spacing: 8) {
                Circle()
                    .fill(client.isConnected ? Color.green : Color.red)
                    .frame(width: 12, height: 12)

                Text(client.isConnected ? "Connecté au serveur Rift" : "Déconnecté")
                    .font(.headline)
            }

            // Boutons
            HStack {
                Button("Connect") {
                    client.connect()
                }
                .disabled(client.isConnected)

                Button("Disconnect") {
                    client.disconnect()
                }
                .disabled(!client.isConnected)

                Button("Send test telemetry") {
                    client.sendTestTelemetry()
                }
                .disabled(!client.isConnected)
            }

            // Erreur
            if let error = client.lastError {
                Text("Erreur: \(error)")
                    .font(.caption)
                    .foregroundColor(.red)
            }

            // Logs
            Text("Logs")
                .font(.headline)

            ScrollView {
                LazyVStack(alignment: .leading, spacing: 4) {
                    ForEach(client.logLines.indices, id: \.self) { idx in
                        Text(client.logLines[idx])
                            .font(.system(size: 12, design: .monospaced))
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            .background(Color.gray.opacity(0.15))
            .cornerRadius(8)

            Spacer()
        }
        .padding()
    }
}

#Preview {
    WebsocketView()
}
