
import XCTest
@testable import scenography_monitor

class ProjectManagerTests: XCTestCase {

    func testProjectDataSerialization() throws {
        // Mock Data
        let mockRoutes = ["sound1.wav": 1, "sound2.wav": 2]
        // Bindings
        let mockBinding = SoundTrigger.BindingConfig(jsonKey: "test", soundName: "sound1.wav", targetValue: "true")
        
        // Buses
        var mockBus = SoundManager.AudioBus(id: 1, name: "TestBus")
        mockBus.volume = 0.5
        
        // Create Data Object
        let projectData = ProjectManager.ProjectData(
            version: "1.0",
            timestamp: Date(),
            soundRoutes: mockRoutes,
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
        XCTAssertEqual(decodedData.version, "1.0")
        XCTAssertEqual(decodedData.soundRoutes["sound1.wav"], 1)
        XCTAssertEqual(decodedData.bindings.count, 1)
        XCTAssertEqual(decodedData.bindings.first?.jsonKey, "test")
        XCTAssertEqual(decodedData.audioBuses.first?.name, "TestBus")
        XCTAssertEqual(decodedData.audioBuses.first?.volume, 0.5)
    }
}
