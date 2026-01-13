//
//  main.swift
//  flux-dev-kontext-local
//
//  Created by eth on 13/01/2026.
//

import Foundation
import FluxSwift
import Hub
import MLX

// --- Helpers ---

func log(_ message: String, emoji: String = "ℹ️", terminator: String = "\n") {
    let formatter = DateFormatter()
    formatter.dateFormat = "HH:mm:ss.SSS"
    let timestamp = formatter.string(from: Date())
    print("\(emoji) [\(timestamp)] \(message)", terminator: terminator)
}

func unpackLatents(_ latents: MLXArray, height: Int, width: Int) -> MLXArray {
    let reshaped = latents.reshaped(1, height / 16, width / 16, 16, 2, 2)
    let transposed = reshaped.transposed(0, 1, 4, 2, 5, 3)
    return transposed.reshaped(1, height / 16 * 2, width / 16 * 2, 16)
}

func savePPM(array: MLXArray, path: String) {
    let h = array.dim(0)
    let w = array.dim(1)
    
    // asArray returns [T]
    let data = array.asArray(UInt8.self)
    
    let header = "P6\n\(w) \(h)\n255\n"
    guard let headerData = header.data(using: .utf8) else { return }
    
    let url = URL(fileURLWithPath: path)
    do {
        var fileData = Data()
        fileData.append(headerData)
        let binaryData = Data(data) 
        fileData.append(binaryData)
        try fileData.write(to: url)
        log("Saved PPM image to \(path)", emoji: "💾")
    } catch {
        log("Failed to save image: \(error)", emoji: "❌")
    }
}

/// Create a simple test input image (gradient pattern)
func createTestImage(width: Int, height: Int) -> MLXArray {
    log("Creating test input image (\(width)x\(height))...", emoji: "🎨")
    
    // Create a simple gradient image for testing
    var pixels: [Float] = []
    for y in 0..<height {
        for x in 0..<width {
            let r = Float(x) / Float(width)      // Red gradient horizontal
            let g = Float(y) / Float(height)     // Green gradient vertical
            let b: Float = 0.5                   // Constant blue
            pixels.append(r)
            pixels.append(g)
            pixels.append(b)
        }
    }
    
    // Create MLXArray with shape [H, W, C] and normalize to [-1, 1]
    let array = MLXArray(pixels, [height, width, 3])
    let normalized = array * 2 - 1  // Convert from [0,1] to [-1,1]
    return normalized
}


@main
struct FluxTest {
    static func main() async {
        do {
            log("Starting Flux Kontext Test...", emoji: "🚀")
            
            // 1. Define Model and Parameters
            let repoId = "mzbac/flux1.kontext.4bit.mlx"
            let outputFilename = "flux_output.ppm" 
            
            log("Target Model: \(repoId)", emoji: "🎯")
            log("Note: Kontext is an image-to-image model - requires input image", emoji: "📌")
            
            // 2. Download/Locate Model
            log("Checking model availability...", emoji: "🔍")
            let modelDir = try await HubApi().snapshot(from: repoId)
            log("Model available at: \(modelDir.path)", emoji: "📂")
            
            // 3. Load Quantized Model
            log("Loading quantized Kontext model...", emoji: "🧠")
            let loadStart = Date()
            
            // Load the model as Kontext type
            let baseModel = try await FLUX.loadQuantized(
                from: modelDir.path, 
                modelType: "kontext"
            )
            
            // Cast to KontextImageToImageGenerator for image-to-image generation
            guard let generator = baseModel as? KontextImageToImageGenerator else {
                log("Error: Loaded model does not conform to KontextImageToImageGenerator", emoji: "❌")
                return
            }
            
            let loadTime = Date().timeIntervalSince(loadStart)
            log("Model loaded in \(String(format: "%.2f", loadTime))s", emoji: "✅")
            
            // 4. Create Input Image
            let inputWidth = 512
            let inputHeight = 512
            let inputImage = createTestImage(width: inputWidth, height: inputHeight)
            
            // 5. Configuration
            log("Configuring parameters...", emoji: "⚙️")
            
            // Use Kontext default parameters (30 steps, shift sigmas)
            var params = FluxConfiguration.flux1KontextDev.defaultParameters()
            params.prompt = "Transform this into a futuristic cyberpunk scene with neon lights"
            params.width = inputWidth
            params.height = inputHeight
            params.numInferenceSteps = 30  // Recommended for Kontext

            log("Prompt: \"\(params.prompt)\"", emoji: "📝")
            log("Size: \(params.width)x\(params.height)", emoji: "📏")
            log("Steps: \(params.numInferenceSteps)", emoji: "👣")
            
            // 6. Generate using Kontext (image-to-image)
            log("Generation started (image-to-image)...", emoji: "🎨")
            let genStart = Date()
            
            // Use generateKontextLatents for image-to-image transformation
            var latentsSequence = generator.generateKontextLatents(
                image: inputImage,
                parameters: params
            )
            
            var lastXt: MLXArray?
            var stepCount = 0
            while let xt = latentsSequence.next() {
                stepCount += 1
                eval(xt)  // Ensure computation is complete before continuing
                print(".", terminator: "")
                fflush(stdout)
                lastXt = xt
            }
            print("")
            log("Completed \(stepCount) denoising steps", emoji: "✓")
            
            guard let finalLatents = lastXt else {
                log("Failed to generate latents", emoji: "❌")
                return
            }
            
            // 7. Decode
            log("Decoding latents...", emoji: "🖼️")
            let unpacked = unpackLatents(finalLatents, height: params.height, width: params.width)
            let decoded = generator.decode(xt: unpacked)
            
            // 8. Post-process
            let squeezed = decoded.squeezed()
            // Clamp to [0, 1] then scale to [0, 255]
            let clamped = MLX.clip(squeezed, min: 0, max: 1)
            let raster = (clamped * 255).asType(.uint8)
            
            // 9. Save Image
            savePPM(array: raster, path: outputFilename)
            
            let genTime = Date().timeIntervalSince(genStart)
            
            // 10. Report
            log("Generation complete!", emoji: "✨")
            log("Total Generation Time: \(String(format: "%.2f", genTime))s", emoji: "⏱️")
            log("Output saved to: \(outputFilename)", emoji: "📁")
            log("Tip: Convert PPM to PNG with: convert \(outputFilename) output.png", emoji: "💡")
            
        } catch {
            log("An error occurred: \(error)", emoji: "💥")
        }
    }
}
