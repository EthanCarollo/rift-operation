//
//  RobotView.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import SwiftUI

struct RobotView: View {
    @EnvironmentObject var wsManager: WebSocketManager

    // MARK: - UI State
    @State private var bluetoothName: String = "RV-7B4C"
    @State private var robot: Robot? = nil

    // Sensor & Battery
    @State private var sensorText: String = "Waiting for data..."
    @State private var lastActionText: String = "READY" // New state for event log
    @State private var batteryText: String = "--"
    @State private var batteryIcon: String = "battery.0"

    // Debug Timer
    @State private var interactionTimer: Timer?
    @State private var pressDuration: Double = 0.0
    @State private var isInteracting: Bool = false
    @State private var interactionsLog: [String] = []

    // Design
    @State private var selectedColor: RobotColor = .off
    
    // Rift Step Log History
    @State private var riftStepLog: [String] = ["[SYSTEM] Waiting for rift_step_1..."]
    @State private var currentStep: Int = 1 // Track which step we're on (1, 2, or 3)

    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                colors: [.black, Color(hex: 0x1a1a2e), Color(hex: 0x16213e)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            GeometryReader { geometry in
                let isLandscape = geometry.size.width > 600 // Simple heuristic for Mac/iPad vs Phone Portrait
                
                VStack(spacing: 30) {
                    
                    // Header (Shared)
                    headerView
                    
                    if let rob = robot, rob.isConnected {
                        if isLandscape {
                            // Landscape / Mac Layout: Side by Side
                            HStack(alignment: .top, spacing: 20) {
                                controlsPanel
                                telemetryPanel
                                    .frame(width: 300)
                            }
                            .padding(.horizontal)
                        } else {
                            // Portrait / iPhone Layout: Vertical Stack
                            ScrollView {
                                VStack(spacing: 20) {
                                    controlsPanel
                                    telemetryPanel
                                }
                                .padding(.horizontal)
                                .padding(.bottom, 20)
                            }
                        }
                    } else {
                        connectingView
                    }
                    
                    if isLandscape { Spacer() }
                }
            }
        }
        .onAppear {
            createAndConnectRobot()
        }
        .onReceive(NotificationCenter.default.publisher(for: .riftStepReceived)) { _ in
            guard let rob = self.robot, rob.isConnected else { return }
            
            // Log received
            riftStepLog.append("[RECEIVED] launch_close_rift_step_\(currentStep) = true")
            print("Rift Step \(currentStep) Received!")
            
            // Execute movement - just forward, no repositioning
            rob.forward(speed: 100)
            
            // After 2.3s, stop movement (calibrated for 1/3 curtain closure)
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.9) {
                rob.forward(speed: 0)
                
                // Log completed
                if currentStep == 3 {
                    riftStepLog.append("[COMPLETED] launch_close_rift (ALL STEPS DONE)")
                } else {
                    riftStepLog.append("[COMPLETED] launch_close_rift_step_\(currentStep)")
                    currentStep += 1
                    riftStepLog.append("[WAITING] Waiting for rift_step_\(currentStep)...")
                }
            }
        }
    }

    // MARK: - Subviews
    
    private var headerView: some View {
        HStack {
            Image(systemName: "dot.radiowaves.left.and.right")
                .foregroundColor(.blue)
                .font(.largeTitle)
            Text("OPERATOR RVR")
                .font(.system(size: 28, weight: .bold, design: .monospaced))
                .foregroundColor(.white)
                .shadow(color: .blue.opacity(0.8), radius: 10, x: 0, y: 0)
            Spacer()
            
            // Connection Status
            HStack(spacing: 15) {
                // WS Status
                HStack {
                    Image(systemName: "server.rack")
                        .font(.caption)
                        .foregroundColor(wsManager.connectionStatus == .connected ? .cyan : (wsManager.connectionStatus == .connecting ? .yellow : .gray))
                    Circle()
                        .fill(wsManager.connectionStatus == .connected ? Color.cyan : (wsManager.connectionStatus == .connecting ? Color.yellow : Color.red))
                        .frame(width: 8, height: 8)
                        .shadow(color: wsManager.connectionStatus == .connected ? .cyan : (wsManager.connectionStatus == .connecting ? .yellow : .red), radius: 5)
                    Text("WS")
                        .font(.caption.bold())
                        .foregroundColor(.white.opacity(0.8))
                }
                .padding(6)
                .background(.ultraThinMaterial)
                .cornerRadius(15)

                // Robot Status
                HStack {
                    Circle()
                        .fill(robot?.isConnected == true ? Color.green : Color.red)
                        .frame(width: 8, height: 8)
                        .shadow(color: robot?.isConnected == true ? .green : .red, radius: 5)
                    Text(robot?.isConnected == true ? "RVR" : "NO LINK")
                        .font(.caption.bold())
                        .foregroundColor(.white.opacity(0.8))
                }
                .padding(8)
                .background(.ultraThinMaterial)
                .cornerRadius(20)
            }
        }
        .padding(.horizontal)
        .padding(.top, 20)
    }
    
    private var controlsPanel: some View {
        // LEFT PANEL: CONTROLS
        VStack(spacing: 20) {
            Text("MANUAL OVERRIDE")
                .font(.caption)
                .foregroundColor(.gray)
                .frame(maxWidth: .infinity, alignment: .leading)

            Spacer()

            if let rob = robot {
                // Directional Pad
                VStack(spacing: 15) {
                    ControlButton(icon: "arrow.up", label: "FORWARD", color: .cyan) {
                        startInteraction(cmd: "Forward")
                        rob.forward(speed: 100)
                    } onPressRelease: {
                        stopInteraction()
                    }

                    HStack(spacing: 20) {
                        ControlButton(icon: "arrow.turn.up.left", label: "LEFT", color: .purple) {
                            startInteraction(cmd: "Left")
                            rob.turn(degrees: -15)
                        } onPressRelease: { stopInteraction() }

                        ControlButton(icon: "stop.fill", label: "HALT", color: .red) {
                            startInteraction(cmd: "Stop")
                            rob.stop()
                        } onPressRelease: { stopInteraction() }

                        ControlButton(icon: "arrow.turn.up.right", label: "RIGHT", color: .purple) {
                            startInteraction(cmd: "Right")
                            rob.turn(degrees: 15)
                        } onPressRelease: { stopInteraction() }
                    }

                    ControlButton(icon: "arrow.down", label: "REVERSE", color: .cyan) {
                        startInteraction(cmd: "Reverse")
                        rob.backward(speed: 80)
                    } onPressRelease: { stopInteraction() }
                }
            }
            
            Spacer()
            
            // LED Control
            if let rob = robot {
                VStack(alignment: .leading, spacing: 10) {
                    Text("LIGHTING SYSTEM")
                        .font(.caption)
                        .foregroundColor(.gray)
                    
                    HStack {
                        ColorButton(color: .off, selected: $selectedColor, rob: rob)
                        ColorButton(color: .red, selected: $selectedColor, rob: rob)
                        ColorButton(color: .green, selected: $selectedColor, rob: rob)
                        ColorButton(color: .blue, selected: $selectedColor, rob: rob)
                        ColorButton(color: .white, selected: $selectedColor, rob: rob)
                    }
                }
                .padding()
                .background(.ultraThinMaterial)
                .cornerRadius(15)
            }
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(.ultraThinMaterial)
        .cornerRadius(20)
    }
    
    private var telemetryPanel: some View {
        // RIGHT PANEL: TELEMETRY & DEBUG
        VStack(spacing: 20) {
            
            // Debug Timer
            VStack {
                Text("DEBUG TIMER (MS)")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                Text(String(format: "%.0f ms", pressDuration * 1000))
                    .font(.system(size: 40, weight: .bold, design: .monospaced))
                    .foregroundColor(isInteracting ? .yellow : .white)
                    .shadow(color: isInteracting ? .yellow.opacity(0.5) : .clear, radius: 10)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.vertical)
            }
            .padding()
            .background(.ultraThinMaterial)
            .cornerRadius(15)

            // Telemetry
            if let rob = robot {
                VStack(alignment: .leading, spacing: 15) {
                    Text("TELEMETRY STREAM")
                        .font(.caption)
                        .foregroundColor(.gray)
                    
                    HStack {
                        Label(batteryText, systemImage: batteryIcon)
                            .font(.headline)
                            .foregroundColor(batteryText == "Critical" ? .red : .green)
                        Spacer()
                        Text("Heading: \(rob.heading)°")
                            .font(.monospacedDigit(.body)())
                            .foregroundColor(.white)
                    }
                    
                    Divider().background(.white.opacity(0.2))
                    
                    ScrollView {
                        VStack(alignment: .leading, spacing: 2) {
                            ForEach(riftStepLog.indices, id: \.self) { index in
                                Text(riftStepLog[index])
                                    .font(.system(size: 10, design: .monospaced))
                                    .foregroundColor(riftStepLog[index].contains("Completed") ? .green : 
                                                   riftStepLog[index].contains("Received") ? .cyan :
                                                   riftStepLog[index].contains("Waiting") ? .yellow : .white)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                        }
                    }
                    .frame(height: 150)
                }
                .padding()
                .background(.ultraThinMaterial)
                .cornerRadius(15)
            }
            
            Spacer()
        }
    }
    
    private var connectingView: some View {
        VStack {
            Spacer()
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                .scaleEffect(2)
            Text("ESTABLISHING UPLINK...")
                .font(.headline)
                .foregroundColor(.white.opacity(0.7))
                .padding(.top)
            Spacer()
            
            Button("FORCE RECONNECT") {
                createAndConnectRobot()
            }
            .buttonStyle(.bordered)
            .tint(.white)
        }
    }

    // MARK: - Logic

    private func startInteraction(cmd: String) {
        stopInteraction() // Safety clear
        isInteracting = true
        pressDuration = 0.0
        
        // Start Timer
        let startTime = Date()
        interactionTimer = Timer.scheduledTimer(withTimeInterval: 0.01, repeats: true) { _ in
            pressDuration = Date().timeIntervalSince(startTime)
        }
        
    }
    
    private func stopInteraction() {
        isInteracting = false
        interactionTimer?.invalidate()
        interactionTimer = nil
    }
    
    
    // MARK: - Connection

    private func createAndConnectRobot() {
        // Auto using Rover
        let rob = Rover(bluetoothName: bluetoothName)

        rob.onSensorUpdate = { sample in
            DispatchQueue.main.async {
                self.sensorText = """
                POS X  : \(String(format: "%.2f", sample.x))
                POS Y  : \(String(format: "%.2f", sample.y))
                VEL X  : \(String(format: "%.2f", sample.vx))
                VEL Y  : \(String(format: "%.2f", sample.vy))
                YAW    : \(String(format: "%.2f", sample.yaw))
                """
            }
        }

        rob.onBatteryUpdate = { state in
            DispatchQueue.main.async {
                switch state {
                case .ok:
                    batteryText = "OK"
                    batteryIcon = "battery.100"
                case .low:
                    batteryText = "Low"
                    batteryIcon = "battery.25"
                case .critical:
                    batteryText = "Critical"
                    batteryIcon = "exclamationmark.triangle.fill"
                case .unknown:
                    batteryText = "--"
                    batteryIcon = "battery.0"
                }
            }
        }
        
        // Connect hook
        rob.onConnect = {
            print("Connected!")
            print("⚠️ POSITION THE ROVER VERTICALLY NOW! Calibrating in 3 seconds...")
            
            // Give user 3 seconds to position the rover vertically
            DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
                // CRITICAL: Reset heading to calibrate current physical orientation as 0°
                // This works even when rover is vertical!
                rob.resetHeading()
                print("✅ Heading calibrated - vertical position locked as reference!")
            }
        }

        self.robot = rob
        rob.connect()
    }
}

// MARK: - Components

struct ControlButton: View {
    let icon: String
    let label: String
    let color: Color
    let action: () -> Void
    let onPressRelease: () -> Void
    
    var body: some View {
        // Using a complex gesture to simulate Press and Release tracking
        Image(systemName: icon)
            .font(.system(size: 30, weight: .bold))
            .foregroundColor(.white)
            .frame(width: 80, height: 80)
            .background(
                Circle()
                    .fill(
                        LinearGradient(colors: [color.opacity(0.8), color.opacity(0.4)], startPoint: .topLeading, endPoint: .bottomTrailing)
                    )
            )
            .overlay(
                Circle()
                    .stroke(color.opacity(0.6), lineWidth: 2)
            )
            .shadow(color: color.opacity(0.5), radius: 10)
            .onLongPressGesture(minimumDuration: 0.0, perform: {}) { pressing in
                if pressing {
                    action()
                } else {
                    onPressRelease()
                }
            }
    }
}

struct ColorButton: View {
    let color: RobotColor
    @Binding var selected: RobotColor
    let rob: Robot
    
    var displayColor: Color {
        switch color {
        case .off: return .black
        case .white: return .white
        case .red: return .red
        case .green: return .green
        case .blue: return .blue
        default: return .gray
        }
    }
    
    var body: some View {
        Button(action: {
            selected = color
            rob.setMainLED(color: color)
        }) {
            Circle()
                .fill(displayColor)
                .frame(width: 30, height: 30)
                .overlay(
                    Circle()
                        .stroke(Color.white, lineWidth: selected == color ? 3 : 1)
                )
                .shadow(color: displayColor.opacity(0.8), radius: selected == color ? 10 : 0)
        }
        .buttonStyle(.plain)
    }
}

extension Color {
    init(hex: UInt) {
        self.init(
            .sRGB,
            red: Double((hex >> 16) & 0xff) / 255,
            green: Double((hex >> 08) & 0xff) / 255,
            blue: Double((hex >> 00) & 0xff) / 255,
            opacity: 1
        )
    }
}

#Preview {
    RobotView()
        .environmentObject(WebSocketManager())
}
