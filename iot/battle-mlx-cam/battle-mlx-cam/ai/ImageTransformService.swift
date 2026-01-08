//
//  ImageTransformService.swift
//  battle-mlx-cam
//
//  AI service using OpenRouter/Gemini to transform drawings
//

import Foundation
import AppKit

class ImageTransformService: ObservableObject {
    @Published var isProcessing = false
    @Published var lastTransformedImage: NSImage?
    @Published var lastTransformedBase64: String?
    @Published var statusMessage: String = "Ready"
    @Published var processingTime: TimeInterval = 0
    
    private let apiUrl = "https://openrouter.ai/api/v1/chat/completions"
    
    // API Key from environment or hardcoded for testing
    var apiKey: String = ""
    
    init() {
        // Try to load from environment
        if let key = ProcessInfo.processInfo.environment["OPENROUTER_API_KEY"] {
            apiKey = key
        }
    }
    
    func transformDrawing(_ image: CGImage, completion: @escaping (String?) -> Void) {
        guard !apiKey.isEmpty else {
            statusMessage = "❌ No API Key"
            completion(nil)
            return
        }
        
        isProcessing = true
        statusMessage = "🔄 Processing..."
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
                let result = try await callGeminiAPI(base64Image: base64)
                let elapsed = Date().timeIntervalSince(startTime)
                
                DispatchQueue.main.async { [weak self] in
                    self?.isProcessing = false
                    self?.processingTime = elapsed
                    
                    if let imageBase64 = result {
                        self?.lastTransformedBase64 = imageBase64
                        self?.statusMessage = "✅ Done in \(String(format: "%.1fs", elapsed))"
                        
                        // Also create NSImage for preview
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
                    self?.statusMessage = "❌ Error: \(error.localizedDescription)"
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
    
    private func callGeminiAPI(base64Image: String) async throws -> String? {
        var request = URLRequest(url: URL(string: apiUrl)!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("https://github.com/battle-mlx-cam", forHTTPHeaderField: "HTTP-Referer")
        request.setValue("Battle Camera", forHTTPHeaderField: "X-Title")
        request.timeoutInterval = 180
        
        let payload: [String: Any] = [
            "model": "google/gemini-2.5-flash-preview-05-20",
            "modalities": ["image", "text"],
            "messages": [
                [
                    "role": "user",
                    "content": [
                        [
                            "type": "image_url",
                            "image_url": [
                                "url": "data:image/png;base64,\(base64Image)"
                            ]
                        ],
                        [
                            "type": "text",
                            "text": "Transform this drawing into a hyperrealistic digital image with transparent background (no background). Make it look like a magical glowing object. Output as PNG with alpha transparency."
                        ]
                    ]
                ]
            ]
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        
        // Parse response
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let choices = json["choices"] as? [[String: Any]],
              let message = choices.first?["message"] as? [String: Any] else {
            print("[Transform] Failed to parse response")
            return nil
        }
        
        // Look for image in content
        if let content = message["content"] as? [[String: Any]] {
            for item in content {
                if let type = item["type"] as? String, type == "image_url",
                   let imageUrl = item["image_url"] as? [String: Any],
                   let url = imageUrl["url"] as? String,
                   url.hasPrefix("data:") {
                    // Extract base64
                    if let commaIndex = url.firstIndex(of: ",") {
                        let base64 = String(url[url.index(after: commaIndex)...])
                        return base64
                    }
                }
            }
        }
        
        // Check images array
        if let images = message["images"] as? [Any], let firstImage = images.first {
            if let imageStr = firstImage as? String {
                if imageStr.hasPrefix("data:"), let commaIndex = imageStr.firstIndex(of: ",") {
                    return String(imageStr[imageStr.index(after: commaIndex)...])
                }
                return imageStr // Already base64
            }
        }
        
        print("[Transform] No image found in response")
        return nil
    }
}
