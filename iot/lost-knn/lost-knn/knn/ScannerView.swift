//
//  ScannerView.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025.
//

import SwiftUI
import Combine

struct ScannerView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var knnService: KNNService
    
    // NOTE: In a real app, WebSocketManager might be passed down from ContentView.
    // Ideally it should be a shared EnvironmentObject.
    // For this refactor, I will instantiate a new one or better yet, pass it if possible.
    // To match current architecture without changing ContentView signatures too much,
    // I will assume we can access a shared instance or pass it. 
    // However, ContentView creates instances. Let's fix ContentView to pass wsManager down.
    // For now, to keep it simple, I'll rely on a Singleton or pass it.
    // Wait, the best way given the timeframe is to update ContentView to pass wsManager.
    // But since I am editing ScannerView first, let's assume it receives it.
    
    // UPDATE: To avoid build errors before ContentView update, I will add it as an argument.
    // But wait, the previous code didn't pass it.
    // I will add @ObservedObject var wsManager: WebSocketManager to the struct.
    // This requires ContentView to be updated simultaneously or right after.
    
    @ObservedObject var wsManager: WebSocketManager
    
    // Throttler - User requested 1.0s (1000ms)
    let timer = Timer.publish(every: 1.0, on: .main, in: .common).autoconnect()
    
    // State to track if view is active
    @State private var isVisible = false
    
    // Throttling State
    @State private var lastSendTime = Date.distantPast
    @State private var isTaskCompleted = false
    
    var body: some View {
        ZStack {
            // Full Screen Camera
            CameraPreview(cameraManager: cameraManager)
                .ignoresSafeArea()
            
            // Minimal Flower UI
            VStack {
                Spacer()
                
                VStack(spacing: 15) {
                    // Status Header
                    HStack {
                        Image(systemName: "leaf.fill")
                            .foregroundColor(.green)
                        Text(isTaskCompleted ? "Task Complete" : (knnService.trainingSamples.isEmpty ? "Need Training" : "Searching..."))
                            .font(.headline)
                            .foregroundColor(.white)
                    }
                    
                    // Main Result
                    if !knnService.trainingSamples.isEmpty {
                        Text(knnService.predictedLabel)
                            .font(.system(size: 40, weight: .bold, design: .rounded))
                            .foregroundColor(.white)
                            .shadow(radius: 10)
                        
                        // "Lampe" Detection Feedback
                        if knnService.predictedLabel == "Lampe" {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(.yellow)
                                Text("Lampe Detected!")
                                    .font(.headline)
                                    .foregroundColor(.yellow)
                            }
                            .padding(.top, 5)
                            .transition(.scale)
                        }
                    }
                    
                    // Scanning Indicator
                    HStack(spacing: 6) {
                        Circle()
                            .fill(isVisible ? Color.green : Color.gray)
                            .frame(width: 8, height: 8)
                        Text(isVisible ? (isTaskCompleted ? "Done" : "Active") : "Paused")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
                .padding(25)
                .background(.ultraThinMaterial)
                .cornerRadius(25)
                .padding(.horizontal, 40)
                .padding(.bottom, 50)
            }
        }
        .onAppear { isVisible = true }
        .onDisappear { isVisible = false }
        .onReceive(timer) { _ in
            guard isVisible, !isTaskCompleted else { return }
            
            if let frame = cameraManager.getLatestFrame() {
                knnService.predict(buffer: frame)
                
                // Throttle Network Calls (Every 5 seconds)
                if Date().timeIntervalSince(lastSendTime) > 5.0 {
                    if knnService.predictedLabel == "Lampe" {
                         print("[Scanner] Lampe found! Sending Success...")
                         wsManager.sendDrawingRecognized(true)
                         isTaskCompleted = true
                    } else {
                         print("[Scanner] Lampe NOT found. Sending Failure...")
                         wsManager.sendDrawingRecognized(false)
                    }
                    lastSendTime = Date()
                }
            }
        }
    }
}
