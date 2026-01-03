//
//  TrainingView.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI

struct TrainingView: View {
    @ObservedObject var cameraManager: CameraManager
    @ObservedObject var knnService: KNNService
    @State private var labelInput: String = ""
    @State private var isLearning = false
    @FocusState private var isInputFocused: Bool
    // UI Helpers
    @State private var showDetails = false
    
    var body: some View {
        ZStack {
            // Full Screen Camera
            CameraPreview(cameraManager: cameraManager)
                .ignoresSafeArea()
                .onTapGesture {
                    isInputFocused = false
                }
            // UI Overlay
            VStack {
                // Header
                HStack {
                    Text("Training Mode")
                        .font(.custom("AvenirNext-Bold", size: 30))
                        .foregroundColor(.white)
                        .shadow(radius: 5)
                    Spacer()
                    // Show Details Button
                    Button(action: { showDetails.toggle() }) {
                        Image(systemName: "list.bullet.circle.fill")
                            .font(.system(size: 30))
                            .foregroundColor(.white)
                    }
                    // Reset All Button
                    Button(action: {
                        knnService.clearAll()
                    }) {
                        Image(systemName: "trash.circle.fill")
                            .font(.system(size: 30))
                            .foregroundColor(.red)
                            .background(Circle().fill(Color.white))
                    }
                }
                .padding(.horizontal)
                .padding(.top, 60)
                Spacer()
                // Input Card
                VStack(spacing: 20) {
                    TextField("Name this object...", text: $labelInput)
                        .font(.custom("AvenirNext-Medium", size: 20))
                        .padding()
                        .background(Color.black.opacity(0.4))
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.white.opacity(0.3), lineWidth: 1)
                        )
                        .foregroundColor(.white)
                        .accentColor(.yellow)
                        .submitLabel(.done)
                        .focused($isInputFocused)
                    
                    Button(action: {
                        learnObject()
                    }) {
                        HStack {
                            if isLearning {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .black))
                            } else {
                                Image(systemName: "camera.shutter.button.fill")
                                Text("Learn Object")
                            }
                        }
                        .font(.custom("AvenirNext-Bold", size: 18))
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(labelInput.isEmpty ? Color.gray : Color.yellow)
                        .cornerRadius(15)
                    }
                    .disabled(labelInput.isEmpty || isLearning)
                    // Info text
                    let count = knnService.getCounts()[labelInput] ?? 0
                    if !labelInput.isEmpty {
                        Text("Recorded \(count) samples for '\(labelInput)'")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.9))
                    } else {
                        Text("Total samples: \(knnService.trainingSamples.count)")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                }
                .padding(25)
                .background(.ultraThinMaterial)
                .cornerRadius(30)
                .padding(.horizontal)
                .padding(.bottom, 50)
            }
        }
        .sheet(isPresented: $showDetails) {
            SampleListView(knnService: knnService)
        }
    }
    
    private func learnObject() {
        guard let buffer = cameraManager.getLatestFrame(), !labelInput.isEmpty else { return }
        
        isLearning = true
        knnService.learn(buffer: buffer, label: labelInput)
        
        // Haptic Feedback
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            isLearning = false
        }
    }
}

// Helper View for List
struct SampleListView: View {
    @ObservedObject var knnService: KNNService
    
    var counts: [String: Int] {
        knnService.getCounts()
    }
    
    var body: some View {
        NavigationView {
            List {
                ForEach(counts.keys.sorted(), id: \.self) { label in
                    HStack {
                        Text(label).font(.headline)
                        Spacer()
                        Text("\(counts[label] ?? 0) samples").foregroundColor(.secondary)
                    }
                    .swipeActions {
                        Button(role: .destructive) {
                            knnService.deleteObject(label: label)
                        } label: {
                            Label("Delete", systemImage: "trash")
                        }
                    }
                }
            }
            .navigationTitle("Learned Objects")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Text("Total: \(knnService.trainingSamples.count)")
                        .foregroundColor(.secondary)
                }
            }
        }
    }
}
