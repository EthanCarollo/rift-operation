//
//  ImageTransformService.swift
//  battle-mlx-cam
//
//  AI service using fal.ai Flux Kontext Dev for image transformation
//

import Foundation
import AppKit
import Combine

class ImageTransformService: ObservableObject {
    @Published var isProcessing = false
    @Published var lastTransformedImage: NSImage?
    @Published var lastTransformedBase64: String?
    @Published var statusMessage: String = "Ready"
    @Published var processingTime: TimeInterval = 0
    
    // fal.ai API
    private let falApiUrl = "https://queue.fal.run/fal-ai/flux-kontext/dev"
    
    // API Key - FAL_KEY
    var apiKey: String = ""
    
    // Default prompt for transformation
    var prompt: String = "Transform this drawing into a hyperrealistic magical glowing object with transparent background."
    
    init() {
        // Try to load from environment
        if let key = ProcessInfo.processInfo.environment["FAL_KEY"] {
            apiKey = key
        }
    }
    
    func transformDrawing(_ image: CGImage, completion: @escaping (String?) -> Void) {
        guard !apiKey.isEmpty else {
            statusMessage = "❌ No FAL_KEY"
            completion(nil)
            return
        }
        
        isProcessing = true
        statusMessage = "🔄 Submitting to Flux Kontext..."
        let startTime = Date()
        
        // Convert to base64
        guard let base64 = cgImageToBase64(image) else {
            statusMessage = "❌ Failed to encode image"
            isProcessing = false
            completion(nil)
            return
        }
        
        Task {
            do {
                let result = try await callFalAPI(base64Image: base64)
                let elapsed = Date().timeIntervalSince(startTime)
                
                DispatchQueue.main.async { [weak self] in
                    self?.isProcessing = false
                    self?.processingTime = elapsed
                    
                    if let imageBase64 = result {
                        self?.lastTransformedBase64 = imageBase64
                        self?.statusMessage = "✅ Done in \(String(format: "%.1fs", elapsed))"
                        
                        // Create NSImage for preview
                        if let data = Data(base64Encoded: imageBase64) {
                            self?.lastTransformedImage = NSImage(data: data)
                        }
                        
                        completion(imageBase64)
                    } else {
                        self?.statusMessage = "❌ No image returned"
                        completion(nil)
                    }
                }
            } catch {
                DispatchQueue.main.async { [weak self] in
                    self?.isProcessing = false
                    self?.statusMessage = "❌ \(error.localizedDescription)"
                    completion(nil)
                }
            }
        }
    }
    
    private func cgImageToBase64(_ image: CGImage) -> String? {
        let nsImage = NSImage(cgImage: image, size: NSSize(width: image.width, height: image.height))
        guard let tiffData = nsImage.tiffRepresentation,
              let bitmap = NSBitmapImageRep(data: tiffData),
              let pngData = bitmap.representation(using: .png, properties: [:]) else {
            return nil
        }
        return pngData.base64EncodedString()
    }
    
    private func callFalAPI(base64Image: String) async throws -> String? {
        // Create data URI
        let imageDataUri = "data:image/png;base64,\(base64Image)"
        
        var request = URLRequest(url: URL(string: falApiUrl)!)
        request.httpMethod = "POST"
        request.setValue("Key \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 120
        
        let payload: [String: Any] = [
            "prompt": prompt,
            "image_url": imageDataUri,
            "num_inference_steps": 10,
            "guidance_scale": 2.5,
            "num_images": 1,
            "acceleration": "high"
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        // Submit to queue
        let (data, _) = try await URLSession.shared.data(for: request)
        
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw TransformError.invalidResponse
        }
        
        // Check if queued
        if json["status"] as? String == "IN_QUEUE" || json["request_id"] != nil {
            guard let statusUrl = json["status_url"] as? String,
                  let responseUrl = json["response_url"] as? String else {
                throw TransformError.missingUrls
            }
            
            // Poll for completion
            DispatchQueue.main.async { [weak self] in
                self?.statusMessage = "🔄 Processing..."
            }
            
            return try await pollForResult(statusUrl: statusUrl, responseUrl: responseUrl)
        }
        
        // Direct result (shouldn't happen)
        return try await extractImageFromResult(json)
    }
    
    private func pollForResult(statusUrl: String, responseUrl: String) async throws -> String? {
        var request = URLRequest(url: URL(string: statusUrl)!)
        request.setValue("Key \(apiKey)", forHTTPHeaderField: "Authorization")
        request.timeoutInterval = 30
        
        while true {
            let (data, _) = try await URLSession.shared.data(for: request)
            
            guard let statusData = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let status = statusData["status"] as? String else {
                throw TransformError.invalidStatus
            }
            
            switch status {
            case "COMPLETED":
                // Get result
                var resultRequest = URLRequest(url: URL(string: responseUrl)!)
                resultRequest.setValue("Key \(apiKey)", forHTTPHeaderField: "Authorization")
                resultRequest.timeoutInterval = 60
                
                let (resultData, _) = try await URLSession.shared.data(for: resultRequest)
                
                guard let result = try JSONSerialization.jsonObject(with: resultData) as? [String: Any] else {
                    throw TransformError.invalidResponse
                }
                
                return try await extractImageFromResult(result)
                
            case "FAILED", "CANCELLED":
                throw TransformError.requestFailed(status)
                
            default:
                // Still processing, wait
                try await Task.sleep(nanoseconds: 200_000_000) // 0.2s
            }
        }
    }
    
    private func extractImageFromResult(_ result: [String: Any]) async throws -> String? {
        guard let images = result["images"] as? [[String: Any]],
              let firstImage = images.first,
              let imageUrl = firstImage["url"] as? String else {
            throw TransformError.noImage
        }
        
        if imageUrl.hasPrefix("data:") {
            // Data URI - extract base64
            if let commaIndex = imageUrl.firstIndex(of: ",") {
                return String(imageUrl[imageUrl.index(after: commaIndex)...])
            }
            return nil
        } else {
            // Regular URL - download it
            guard let url = URL(string: imageUrl) else {
                throw TransformError.invalidUrl
            }
            
            let (data, _) = try await URLSession.shared.data(from: url)
            return data.base64EncodedString()
        }
    }
    
    enum TransformError: LocalizedError {
        case invalidResponse
        case missingUrls
        case invalidStatus
        case requestFailed(String)
        case noImage
        case invalidUrl
        
        var errorDescription: String? {
            switch self {
            case .invalidResponse: return "Invalid API response"
            case .missingUrls: return "Missing status/response URLs"
            case .invalidStatus: return "Invalid status response"
            case .requestFailed(let status): return "Request failed: \(status)"
            case .noImage: return "No image in response"
            case .invalidUrl: return "Invalid image URL"
            }
        }
    }
}
