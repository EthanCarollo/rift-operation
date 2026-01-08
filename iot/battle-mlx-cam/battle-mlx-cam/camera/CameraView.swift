//
//  CameraView.swift
//  battle-mlx-cam
//
//  Modern iOS26/macOS style camera view
//

import SwiftUI
import AVFoundation

struct CameraView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var wsManager: WebSocketManager
    @StateObject private var transformService = ImageTransformService()
    
    @State private var selectedRole: CameraRole = .nightmare
    @State private var isAutoMode = false
    @State private var autoTimer: Timer?
    
    enum CameraRole: String, CaseIterable {
        case dream = "Dream"
        case nightmare = "Nightmare"
        
        var color: Color {
            switch self {
            case .dream: return .blue
            case .nightmare: return .pink
            }
        }
        
        var icon: String {
            switch self {
            case .dream: return "sun.max.fill"
            case .nightmare: return "moon.fill"
            }
        }
    }
    
    var body: some View {
        ZStack {
            // Gradient background
            LinearGradient(
                colors: [Color(white: 0.05), Color(white: 0.1)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            HStack(spacing: 24) {
                // Left Panel - Camera
                cameraPanel
                
                // Right Panel - AI Output + Controls
                controlPanel
            }
            .padding(24)
        }
        .onDisappear {
            stopAutoMode()
        }
    }
    
    private func startAutoMode() {
        isAutoMode = true
        autoTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            if !transformService.isProcessing, cameraManager.currentFrame != nil {
                transformAndSend()
            }
        }
    }
    
    private func stopAutoMode() {
        isAutoMode = false
        autoTimer?.invalidate()
        autoTimer = nil
    }
    
    // MARK: - Camera Panel
    
    private var cameraPanel: some View {
        VStack(spacing: 16) {
            // Header
            HStack {
                Label("Live Feed", systemImage: "video.fill")
                    .font(.title2.bold())
                    .foregroundStyle(.white)
                
                Spacer()
                
                // Role Selector
                Picker("", selection: $selectedRole) {
                    ForEach(CameraRole.allCases, id: \.self) { role in
                        Label(role.rawValue, systemImage: role.icon)
                            .tag(role)
                    }
                }
                .pickerStyle(.segmented)
                .frame(width: 180)
            }
            
            // Camera Preview
            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(.ultraThinMaterial)
                
                if let frame = cameraManager.currentFrame {
                    Image(decorative: frame, scale: 1.0)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .clipShape(RoundedRectangle(cornerRadius: 16))
                        .padding(4)
                } else {
                    VStack(spacing: 16) {
                        Image(systemName: "camera.viewfinder")
                            .font(.system(size: 56, weight: .thin))
                            .foregroundStyle(.secondary)
                        
                        Text("No Camera")
                            .font(.headline)
                            .foregroundStyle(.secondary)
                        
                        if cameraManager.availableCameras.isEmpty {
                            Text("Check System Settings → Privacy → Camera")
                                .font(.caption)
                                .foregroundStyle(.tertiary)
                        }
                    }
                }
                
                // Processing Overlay
                if transformService.isProcessing {
                    RoundedRectangle(cornerRadius: 20)
                        .fill(.ultraThinMaterial)
                        .overlay {
                            VStack(spacing: 16) {
                                ProgressView()
                                    .scaleEffect(1.5)
                                    .tint(.white)
                                Text("Transforming...")
                                    .font(.headline)
                                    .foregroundStyle(.white)
                            }
                        }
                }
            }
            .overlay {
                RoundedRectangle(cornerRadius: 20)
                    .strokeBorder(
                        LinearGradient(
                            colors: [selectedRole.color, selectedRole.color.opacity(0.3)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 2
                    )
            }
            .frame(maxHeight: .infinity)
            
            // Camera Selector
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(cameraManager.availableCameras, id: \.uniqueID) { camera in
                        CameraChipModern(
                            name: camera.localizedName,
                            isSelected: camera.uniqueID == cameraManager.selectedCamera?.uniqueID,
                            color: selectedRole.color
                        ) {
                            cameraManager.selectCamera(camera)
                        }
                    }
                    
                    if cameraManager.availableCameras.isEmpty {
                        Text("No cameras detected")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .padding(.horizontal)
                    }
                }
            }
            .frame(height: 40)
        }
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Control Panel
    
    private var controlPanel: some View {
        VStack(spacing: 20) {
            // Connection Status Card
            GlassCard {
                HStack {
                    Circle()
                        .fill(wsManager.isConnected ? .green : .red)
                        .frame(width: 10, height: 10)
                    
                    Text(wsManager.isConnected ? "Connected" : "Disconnected")
                        .font(.subheadline.bold())
                    
                    Spacer()
                    
                    Text(wsManager.battleState.uppercased())
                        .font(.caption.bold())
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(.purple.opacity(0.3))
                        .clipShape(Capsule())
                }
            }
            
            // AI Output Preview
            VStack(alignment: .leading, spacing: 12) {
                Label("AI Output", systemImage: "wand.and.stars")
                    .font(.title3.bold())
                    .foregroundStyle(.white)
                
                ZStack {
                    // Transparent checkerboard
                    CheckerboardModern()
                        .clipShape(RoundedRectangle(cornerRadius: 16))
                    
                    if let image = transformService.lastTransformedImage {
                        Image(nsImage: image)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .padding(8)
                            .shadow(color: .purple.opacity(0.5), radius: 20)
                    } else {
                        VStack(spacing: 12) {
                            Image(systemName: "sparkles")
                                .font(.system(size: 40, weight: .thin))
                                .foregroundStyle(.secondary)
                            Text("Transform a drawing")
                                .font(.caption)
                                .foregroundStyle(.tertiary)
                        }
                    }
                }
                .frame(height: 200)
                .overlay {
                    RoundedRectangle(cornerRadius: 16)
                        .strokeBorder(.white.opacity(0.1), lineWidth: 1)
                }
            }
            
            // API Key & Prompt
            GlassCard {
                VStack(alignment: .leading, spacing: 12) {
                    // FAL Key
                    VStack(alignment: .leading, spacing: 6) {
                        Label("FAL_KEY", systemImage: "key.fill")
                            .font(.caption.bold())
                            .foregroundStyle(.secondary)
                        
                        SecureField("Your fal.ai key", text: $transformService.apiKey)
                            .textFieldStyle(.plain)
                            .font(.system(.body, design: .monospaced))
                            .padding(10)
                            .background(.white.opacity(0.05))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                    
                    // Prompt
                    VStack(alignment: .leading, spacing: 6) {
                        Label("Prompt", systemImage: "text.bubble")
                            .font(.caption.bold())
                            .foregroundStyle(.secondary)
                        
                        TextField("Transformation prompt...", text: $transformService.prompt)
                            .textFieldStyle(.plain)
                            .font(.caption)
                            .padding(10)
                            .background(.white.opacity(0.05))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                }
            }
            
            // Status
            if !transformService.statusMessage.isEmpty {
                Text(transformService.statusMessage)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            Spacer()
            
            // Action Buttons
            VStack(spacing: 12) {
                // Auto Mode Toggle
                Button(action: {
                    if isAutoMode {
                        stopAutoMode()
                    } else {
                        startAutoMode()
                    }
                }) {
                    Label(
                        isAutoMode ? "Stop Auto" : "Start Auto",
                        systemImage: isAutoMode ? "stop.circle.fill" : "play.circle.fill"
                    )
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                }
                .buttonStyle(.borderedProminent)
                .tint(isAutoMode ? .orange : .green)
                .disabled(cameraManager.currentFrame == nil || transformService.apiKey.isEmpty)
                
                // Manual Transform Button
                Button(action: transformAndSend) {
                    Label("Transform Once", systemImage: "wand.and.stars")
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                }
                .buttonStyle(.bordered)
                .tint(.purple)
                .disabled(transformService.isProcessing || cameraManager.currentFrame == nil || isAutoMode)
                
                // Camera Control
                HStack(spacing: 12) {
                    Button(action: {
                        if cameraManager.isCapturing {
                            cameraManager.stopCapture()
                        } else {
                            cameraManager.startCapture()
                        }
                    }) {
                        Label(
                            cameraManager.isCapturing ? "Stop Cam" : "Start Cam",
                            systemImage: cameraManager.isCapturing ? "video.slash" : "video"
                        )
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                    }
                    .buttonStyle(.bordered)
                    .tint(cameraManager.isCapturing ? .red : .green)
                    
                    Button(action: { cameraManager.requestCameraAccess() }) {
                        Label("Refresh", systemImage: "arrow.clockwise")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                    }
                    .buttonStyle(.bordered)
                }
            }
        }
        .frame(width: 320)
    }
    
    private func transformAndSend() {
        guard let frame = cameraManager.currentFrame else { return }
        
        transformService.transformDrawing(frame) { base64 in
            if let base64 = base64 {
                let dataUrl = "data:image/png;base64,\(base64)"
                wsManager.sendTransformedImage(dataUrl, role: selectedRole.rawValue.lowercased())
            }
        }
    }
}

// MARK: - Components

struct GlassCard<Content: View>: View {
    @ViewBuilder let content: Content
    
    var body: some View {
        content
            .padding(16)
            .background(.ultraThinMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .overlay {
                RoundedRectangle(cornerRadius: 16)
                    .strokeBorder(.white.opacity(0.1), lineWidth: 1)
            }
    }
}

struct CameraChipModern: View {
    let name: String
    let isSelected: Bool
    let color: Color
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            Text(name)
                .font(.caption.bold())
                .lineLimit(1)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(isSelected ? color.opacity(0.3) : .white.opacity(0.05))
                .foregroundStyle(isSelected ? color : .secondary)
                .clipShape(Capsule())
                .overlay {
                    Capsule()
                        .strokeBorder(isSelected ? color : .clear, lineWidth: 1)
                }
        }
        .buttonStyle(.plain)
    }
}

struct CheckerboardModern: View {
    var body: some View {
        GeometryReader { geo in
            let size: CGFloat = 12
            let cols = Int(ceil(geo.size.width / size))
            let rows = Int(ceil(geo.size.height / size))
            
            Canvas { context, _ in
                for row in 0..<rows {
                    for col in 0..<cols {
                        let isLight = (row + col) % 2 == 0
                        let rect = CGRect(
                            x: CGFloat(col) * size,
                            y: CGFloat(row) * size,
                            width: size,
                            height: size
                        )
                        context.fill(
                            Path(rect),
                            with: .color(isLight ? Color(white: 0.12) : Color(white: 0.08))
                        )
                    }
                }
            }
        }
    }
}
