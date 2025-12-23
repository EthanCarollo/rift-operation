
import XCTest
@testable import scenography_monitor

class ProjectManagerTests: XCTestCase {

    func testProjectDataSerialization() throws {
        // Mock Instances
        let instance = SoundManager.SoundInstance(filename: "sound1.wav")
        let busSamples = [1: [instance]]
        
        // Bindings
        // Note: New bindings require instanceId for full functionality, but targetValue/jsonKey are core.
        let mockBinding = SoundTrigger.BindingConfig(jsonKey: "test", soundName: "sound1.wav", instanceId: instance.id, targetValue: "true")
        
        // Buses
        var mockBus = SoundManager.AudioBus(id: 1, name: "TestBus")
        mockBus.volume = 0.5
        
        // Create Data Object
        let projectData = ProjectManager.ProjectData(
            version: "2.0",
            timestamp: Date(),
            soundRoutes: nil,
            busSamples: busSamples,
            bindings: [mockBinding],
            audioBuses: [mockBus]
        )
        
        // Encode
        let encoder = JSONEncoder()
        let data = try encoder.encode(projectData)
        XCTAssertFalse(data.isEmpty, "Encoded data should not be empty")
        
        // Decode
        let decoder = JSONDecoder()
        let decodedData = try decoder.decode(ProjectManager.ProjectData.self, from: data)
        
        // Assertions
        XCTAssertEqual(decodedData.version, "2.0")
        
        // Verify Instance Data
        XCTAssertNotNil(decodedData.busSamples)
        XCTAssertEqual(decodedData.busSamples?[1]?.first?.filename, "sound1.wav")
        
        // Verify Binding
        XCTAssertEqual(decodedData.bindings.count, 1)
        XCTAssertEqual(decodedData.bindings.first?.jsonKey, "test")
        XCTAssertEqual(decodedData.bindings.first?.instanceId, instance.id)
        
        // Verify Bus
        XCTAssertEqual(decodedData.audioBuses.first?.name, "TestBus")
        XCTAssertEqual(decodedData.audioBuses.first?.volume, 0.5)
    }
}
