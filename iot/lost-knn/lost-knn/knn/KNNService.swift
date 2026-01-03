//
//  KNNService.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI
import CoreML
import Vision
import Combine

struct TrainingSample: Identifiable {
    let id = UUID()
    let label: String
    let vector: [Float]
}

class KNNService: ObservableObject {
    @Published var trainingSamples: [TrainingSample] = []
    @Published var predictedLabel: String = "Scanning..."
    // CoreML Model + Vision Request
    private var model: VNCoreMLModel?
    private var request: VNCoreMLRequest?
    
    init() {
        setupModel()
    }
    
    private func setupModel() {
        do {
            let config = MLModelConfiguration()
            let coreMLModel = try mobilenetv2_truncated(configuration: config)
            self.model = try VNCoreMLModel(for: coreMLModel.model)
            
            if let model = self.model {
                self.request = VNCoreMLRequest(model: model)
                self.request?.imageCropAndScaleOption = .centerCrop
            }
        } catch {
            print("Failed to load Vision model: \(error)")
        }
    }
    
    // MARK: - Public API
    func learn(buffer: CVPixelBuffer, label: String) {
        performRequest(on: buffer) { [weak self] vector in
            guard let self = self, let vector = vector else { return }
            // Log Data (Simulating robust JSON logging)
            let logString = "ID: \(UUID().uuidString.prefix(8)) | Object: \(label) | VectorSize: \(vector.count)"
            print("[KNNService] \(logString)")
            
            DispatchQueue.main.async {
                let sample = TrainingSample(label: label, vector: vector)
                self.trainingSamples.append(sample)
                print("[KNNService] Total Samples: \(self.trainingSamples.count)")
            }
        }
    }
    
    func deleteObject(label: String) {
        DispatchQueue.main.async {
            self.trainingSamples.removeAll { $0.label == label }
            print("[KNNService] Removed all samples for: \(label)")
        }
    }
    
    func clearAll() {
        DispatchQueue.main.async {
            self.trainingSamples.removeAll()
            print("[KNNService] Cleared all training data")
        }
    }
    
    func getCounts() -> [String: Int] {
        var counts: [String: Int] = [:]
        for sample in trainingSamples {
            counts[sample.label, default: 0] += 1
        }
        return counts
    }
    
    func predict(buffer: CVPixelBuffer) {
        if trainingSamples.isEmpty {
            DispatchQueue.main.async {
                 if self.predictedLabel != "Need Training Data" {
                     self.predictedLabel = "Need Training Data"
                 }
            }
            return
        }
        
        performRequest(on: buffer) { [weak self] vector in
            guard let self = self, let vector = vector else { return }
            
            var bestLabel = "Unknown"
            var minDistance: Float = .greatestFiniteMagnitude
            
            for sample in self.trainingSamples {
                let dist = self.distance(v1: vector, v2: sample.vector)
                if dist < minDistance {
                    minDistance = dist
                    bestLabel = sample.label
                }
            }
            // Console Log for Scanner
            let confidence = String(format: "%.2f", minDistance)
            print("[Scanner] Pred: \(bestLabel) | Dist: \(confidence) | Best Match: \(minDistance < 100 ? "Yes" : "No")")
            
            DispatchQueue.main.async {
                self.predictedLabel = bestLabel
            }
        }
    }
    
    // MARK: - Internal Logic
    private func performRequest(on buffer: CVPixelBuffer, completion: @escaping ([Float]?) -> Void) {
        guard let request = self.request else { return }
        
        DispatchQueue.global(qos: .userInitiated).async {
            let handler = VNImageRequestHandler(cvPixelBuffer: buffer, options: [:])
            do {
                try handler.perform([request])
                
                guard let observations = request.results as? [VNCoreMLFeatureValueObservation],
                      let firstObs = observations.first,
                      let multiArray = firstObs.featureValue.multiArrayValue else {
                    completion(nil)
                    return
                }
                
                let vector = self.convertMultiArrayToFloat(multiArray)
                completion(vector)
            } catch {
                print("Vision request failed: \(error)")
                completion(nil)
            }
        }
    }
    
    private func convertMultiArrayToFloat(_ multiArray: MLMultiArray) -> [Float] {
        var array: [Float] = []
        let count = multiArray.count
        multiArray.withUnsafeBufferPointer(ofType: Float.self) { ptr in
            if let baseAddress = ptr.baseAddress {
                array = Array(UnsafeBufferPointer(start: baseAddress, count: count))
            } else {
                for i in 0..<count {
                    array.append(multiArray[i].floatValue)
                }
            }
        }
        return array
    }
    
    private func distance(v1: [Float], v2: [Float]) -> Float {
        var sum: Float = 0
        let count = min(v1.count, v2.count)
        for i in 0..<count {
            let diff = v1[i] - v2[i]
            sum += diff * diff
        }
        return sqrt(sum)
    }
}
