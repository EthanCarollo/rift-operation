//
//  CameraManager.swift
//  battle-mlx-cam
//
//  Manages multiple camera captures for macOS
//

import SwiftUI
import Combine
import AVFoundation
import CoreImage

class CameraManager: NSObject, ObservableObject {
    @Published var currentFrame: CGImage?
    @Published var availableCameras: [AVCaptureDevice] = []
    @Published var selectedCamera: AVCaptureDevice?
    @Published var isCapturing = false
    @Published var cameraName: String = "None"
    
    private var captureSession: AVCaptureSession?
    private var videoOutput: AVCaptureVideoDataOutput?
    private let processingQueue = DispatchQueue(label: "camera.processing", qos: .userInteractive)
    private let context = CIContext()
    
    override init() {
        super.init()
        discoverCameras()
    }
    
    func discoverCameras() {
        let discoverySession = AVCaptureDevice.DiscoverySession(
            deviceTypes: [.builtInWideAngleCamera, .externalUnknown],
            mediaType: .video,
            position: .unspecified
        )
        availableCameras = discoverySession.devices
        print("[CameraManager] Found \(availableCameras.count) cameras:")
        for (index, cam) in availableCameras.enumerated() {
            print("  [\(index)] \(cam.localizedName)")
        }
        
        // Select first camera by default
        if let first = availableCameras.first {
            selectCamera(first)
        }
    }
    
    func selectCamera(_ device: AVCaptureDevice) {
        // Stop current session
        if isCapturing {
            stopCapture()
        }
        
        selectedCamera = device
        cameraName = device.localizedName
        print("[CameraManager] Selected: \(device.localizedName)")
        
        // Start with new camera
        startCapture()
    }
    
    func startCapture() {
        guard let camera = selectedCamera else {
            print("[CameraManager] No camera selected")
            return
        }
        guard !isCapturing else { return }
        
        captureSession = AVCaptureSession()
        captureSession?.sessionPreset = .high
        
        do {
            let input = try AVCaptureDeviceInput(device: camera)
            if captureSession?.canAddInput(input) == true {
                captureSession?.addInput(input)
            }
            
            videoOutput = AVCaptureVideoDataOutput()
            videoOutput?.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
            videoOutput?.setSampleBufferDelegate(self, queue: processingQueue)
            videoOutput?.alwaysDiscardsLateVideoFrames = true
            
            if let output = videoOutput, captureSession?.canAddOutput(output) == true {
                captureSession?.addOutput(output)
            }
            
            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                self?.captureSession?.startRunning()
                DispatchQueue.main.async {
                    self?.isCapturing = true
                }
            }
            
            print("[CameraManager] Started capture")
            
        } catch {
            print("[CameraManager] Failed to setup camera: \(error)")
        }
    }
    
    func stopCapture() {
        captureSession?.stopRunning()
        captureSession = nil
        videoOutput = nil
        isCapturing = false
        currentFrame = nil
        print("[CameraManager] Stopped capture")
    }
}

// MARK: - AVCaptureVideoDataOutputSampleBufferDelegate

extension CameraManager: AVCaptureVideoDataOutputSampleBufferDelegate {
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return }
        
        DispatchQueue.main.async { [weak self] in
            self?.currentFrame = cgImage
        }
    }
}
