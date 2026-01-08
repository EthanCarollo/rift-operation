//
//  CameraView.swift
//  battle-mlx-cam
//
//  Camera preview and selection view
//

import SwiftUI
import AVFoundation

struct CameraView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var wsManager: WebSocketManager
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 20) {
                // Header
                HStack {
                    Text("Camera")
                        .font(.system(size: 34, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    Spacer()
                    
                    // Connection Status
                    HStack(spacing: 6) {
                        Circle()
                            .fill(wsManager.isConnected ? Color.green : Color.red)
                            .frame(width: 8, height: 8)
                        Text(wsManager.battleState.uppercased())
                            .font(.caption.bold())
                            .foregroundColor(.purple)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color(white: 0.1))
                    .clipShape(Capsule())
                }
                .padding(.horizontal)
                .padding(.top, 20)
                
                // Camera Preview
                ZStack {
                    if let frame = cameraManager.currentFrame {
                        Image(decorative: frame, scale: 1.0)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .cornerRadius(16)
                    } else {
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color(white: 0.1))
                            .overlay(
                                VStack(spacing: 12) {
                                    Image(systemName: "camera.fill")
                                        .font(.system(size: 48))
                                        .foregroundColor(.gray)
                                    Text("No Camera Feed")
                                        .foregroundColor(.gray)
                                }
                            )
                    }
                }
                .frame(maxHeight: 400)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.purple.opacity(0.5), lineWidth: 2)
                )
                .padding(.horizontal)
                
                // Camera Selection
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("AVAILABLE CAMERAS")
                            .font(.caption.bold())
                            .foregroundColor(.gray)
                        Spacer()
                        Button(action: { cameraManager.discoverCameras() }) {
                            Image(systemName: "arrow.clockwise")
                                .foregroundColor(.gray)
                        }
                        .buttonStyle(.plain)
                    }
                    
                    if cameraManager.availableCameras.isEmpty {
                        Text("No cameras found")
                            .foregroundColor(.gray)
                            .padding()
                    } else {
                        ForEach(cameraManager.availableCameras, id: \.uniqueID) { camera in
                            CameraRow(
                                camera: camera,
                                isSelected: camera.uniqueID == cameraManager.selectedCamera?.uniqueID
                            ) {
                                cameraManager.selectCamera(camera)
                            }
                        }
                    }
                }
                .padding()
                .background(Color(white: 0.1))
                .cornerRadius(16)
                .padding(.horizontal)
                
                // Controls
                HStack(spacing: 15) {
                    Button(action: {
                        if cameraManager.isCapturing {
                            cameraManager.stopCapture()
                        } else {
                            cameraManager.startCapture()
                        }
                    }) {
                        HStack {
                            Image(systemName: cameraManager.isCapturing ? "stop.fill" : "play.fill")
                            Text(cameraManager.isCapturing ? "Stop" : "Start")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(cameraManager.isCapturing ? Color.red : Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .buttonStyle(.plain)
                    
                    Button(action: {
                        // Send test recognition
                        wsManager.sendDrawingRecognised(dream: true, nightmare: nil)
                    }) {
                        HStack {
                            Image(systemName: "checkmark.circle")
                            Text("Test Dream")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .buttonStyle(.plain)
                    .disabled(!wsManager.isConnected)
                    
                    Button(action: {
                        wsManager.sendDrawingRecognised(dream: nil, nightmare: true)
                    }) {
                        HStack {
                            Image(systemName: "checkmark.circle")
                            Text("Test Nightmare")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.pink)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .buttonStyle(.plain)
                    .disabled(!wsManager.isConnected)
                }
                .padding(.horizontal)
                
                Spacer()
            }
        }
    }
}

// MARK: - Camera Row

struct CameraRow: View {
    let camera: AVCaptureDevice
    let isSelected: Bool
    let onSelect: () -> Void
    
    var body: some View {
        Button(action: onSelect) {
            HStack {
                Image(systemName: isBuiltIn ? "laptopcomputer" : "video.fill")
                    .foregroundColor(isSelected ? .purple : .gray)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(camera.localizedName)
                        .font(.system(.body, design: .default))
                        .foregroundColor(.white)
                    Text(camera.uniqueID.prefix(20) + "...")
                        .font(.caption2)
                        .foregroundColor(.gray)
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.purple)
                }
            }
            .padding(12)
            .background(isSelected ? Color.purple.opacity(0.2) : Color(white: 0.05))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isSelected ? Color.purple : Color.clear, lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
    
    var isBuiltIn: Bool {
        camera.localizedName.lowercased().contains("facetime") ||
        camera.localizedName.lowercased().contains("built")
    }
}
