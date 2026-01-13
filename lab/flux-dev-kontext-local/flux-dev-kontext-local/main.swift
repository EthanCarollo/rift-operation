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
        log("Saved PPM image to \(path) (View specific viewers or convert)", emoji: "💾")
    } catch {
        log("Failed to save image: \(error)", emoji: "❌")
    }
}


@main
struct FluxTest {
    static func main() async {
        do {
            log("Starting Flux Test...", emoji: "🚀")
            
            // 1. Define Model and Parameters
            let repoId = "mzbac/flux1.kontext.4bit.mlx"
            let outputFilename = "flux_output.ppm" 
            
            log("Target Model: \(repoId)", emoji: "🎯")
            
            // 2. Download/Locate Model
            log("Checking model availability...", emoji: "🔍")
            let modelDir = try await HubApi().snapshot(from: repoId)
            log("Model available at: \(modelDir.path)", emoji: "📂")
            
            // 3. Load Quantized Model
            log("Loading quantized model (Type: kontext)...", emoji: "🧠")
            let loadStart = Date()
            
            // Load the model. Returns FLUX.
            // We cast it to TextToImageGenerator (or ImageToImageGenerator if available/needed)
            let baseModel = try await FLUX.loadQuantized(
                from: modelDir.path, 
                modelType: "kontext" 
            )
            
            guard let generator = baseModel as? TextToImageGenerator else {
                log("Error: Loaded model does not conform to TextToImageGenerator", emoji: "❌")
                return
            }
            
            let loadTime = Date().timeIntervalSince(loadStart)
            log("Model loaded in \(String(format: "%.2f", loadTime))s", emoji: "✅")
            
            // 4. Configuration
            log("Configuring parameters...", emoji: "⚙️")
            // Use defaults from Flux1Dev configuration as fallback/base
            var params = FluxConfiguration.flux1Dev.defaultParameters()
            params.prompt = "A futuristic city with neon lights, high detail, 8k resolution"
            params.width = 512
            params.height = 512
            params.numInferenceSteps = 4 

            log("Prompt: \"\(params.prompt)\"", emoji: "📝")
            log("Size: \(params.width)x\(params.height)", emoji: "📏")
            log("Steps: \(params.numInferenceSteps)", emoji: "👣")
            
            // 5. Generate
            log("Generaton started...", emoji: "🎨")
            let genStart = Date()
            
            // Generate latents sequence
            let latentsSequence = generator.generateLatents(parameters: params)
            
            var lastXt: MLXArray?
            for xt in latentsSequence {
                lastXt = xt
                print(".", terminator: "")
                fflush(stdout)
            }
            print("")
            
            guard let finalLatents = lastXt else {
                log("Failed to generate latents", emoji: "❌")
                return
            }
            
            // Decode
            log("Decoding latents...", emoji: "🖼️")
            let unpacked = unpackLatents(finalLatents, height: params.height, width: params.width)
            let decoded = generator.decode(xt: unpacked)
            
            // Post-process
            let squeezed = decoded.squeezed()
            let raster = (squeezed * 255).asType(.uint8)
            
            // Save Image
            savePPM(array: raster, path: outputFilename)
            
            let genTime = Date().timeIntervalSince(genStart)
            
            // 6. Report
            log("Generation complete!", emoji: "✨")
            log("Total Generation Time: \(String(format: "%.2f", genTime))s", emoji: "⏱️")
            
        } catch {
            log("An error occurred: \(error)", emoji: "💥")
        }
    }
}
