//
//  CameraManager.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI
import AVFoundation
import Combine
import UIKit

// Separate actor-independent handler for frame data
private class FrameHandler: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate, @unchecked Sendable {
    private var _currentFrame: CVPixelBuffer?
    private let frameLock = NSLock()
    
    func getLatestFrame() -> CVPixelBuffer? {
        frameLock.lock()
        defer { frameLock.unlock() }
        return _currentFrame
    }
    
    nonisolated func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let buffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        frameLock.lock()
        _currentFrame = buffer
        frameLock.unlock()
    }
}

class CameraManager: NSObject, ObservableObject {
    @Published var session = AVCaptureSession()
    
    private let frameHandler = FrameHandler()
    private let videoOutput = AVCaptureVideoDataOutput()
    private let queue = DispatchQueue(label: "camera.queue", qos: .userInitiated)
    
    override init() {
        super.init()
        setupCamera()
    }
    
    func setupCamera() {
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            self.session.beginConfiguration()
            
            if self.session.canSetSessionPreset(.vga640x480) {
                self.session.sessionPreset = .vga640x480
            }
            
            guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
                  let input = try? AVCaptureDeviceInput(device: device) else {
                print("Failed to get camera device")
                return
            }
            
            if self.session.canAddInput(input) {
                self.session.addInput(input)
            }
            
            self.videoOutput.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: Int(kCVPixelFormatType_32BGRA)]
            // Set delegate to our helper FrameHandler
            self.videoOutput.setSampleBufferDelegate(self.frameHandler, queue: self.queue)
            self.videoOutput.alwaysDiscardsLateVideoFrames = true
            
            if self.session.canAddOutput(self.videoOutput) {
                self.session.addOutput(self.videoOutput)
            }
            
            self.session.commitConfiguration()
        }
    }
    
    func start() {
        guard !session.isRunning else { return }
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.session.startRunning()
        }
    }
    
    func stop() {
        guard session.isRunning else { return }
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.session.stopRunning()
        }
    }
    
    func getLatestFrame() -> CVPixelBuffer? {
        return frameHandler.getLatestFrame()
    }
}

// MARK: - Robust Preview View
class PreviewView: UIView {
    // Explicitly override layerClass
    override class var layerClass: AnyClass {
        return AVCaptureVideoPreviewLayer.self
    }
    
    var videoPreviewLayer: AVCaptureVideoPreviewLayer {
        return layer as! AVCaptureVideoPreviewLayer
    }
    
    // Ensure Layout
    override func layoutSubviews() {
        super.layoutSubviews()
        videoPreviewLayer.frame = bounds
    }
}

struct CameraPreview: UIViewRepresentable {
    @ObservedObject var cameraManager: CameraManager
    
    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        view.backgroundColor = .black // Black background until feed appears
        view.videoPreviewLayer.videoGravity = .resizeAspectFill
        view.videoPreviewLayer.session = cameraManager.session
        updateOrientation(for: view.videoPreviewLayer)
        return view
    }
    
    func updateUIView(_ uiView: PreviewView, context: Context) {
        // ALWAYS ensure session is attached. SwiftUI might recreate the struct but keep the UIView.
        if uiView.videoPreviewLayer.session != cameraManager.session {
            uiView.videoPreviewLayer.session = cameraManager.session
        }
        updateOrientation(for: uiView.videoPreviewLayer)
    }
    
    private func updateOrientation(for layer: AVCaptureVideoPreviewLayer) {
        guard let connection = layer.connection else { return }
        
        if #available(iOS 17.0, *) {
            if connection.isVideoRotationAngleSupported(90) {
                connection.videoRotationAngle = 90
            }
        } else {
            if connection.isVideoOrientationSupported {
                connection.videoOrientation = .portrait
            }
        }
    }
}
