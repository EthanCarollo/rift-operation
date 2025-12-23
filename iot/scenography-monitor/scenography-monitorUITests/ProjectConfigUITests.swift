
import XCTest

class ProjectConfigUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testConfigButtonsExist() throws {
        // Launch App
        let app = XCUIApplication()
        app.launch()
        
        // Check for LOAD button
        let loadButton = app.buttons["LOAD"]
        XCTAssertTrue(loadButton.exists, "LOAD button should exist in toolbar")
        
        // Check for SAVE button
        let saveButton = app.buttons["SAVE"]
        XCTAssertTrue(saveButton.exists, "SAVE button should exist in toolbar")
        
        // Check for Audio Devices button
        let audioDevices = app.buttons["AUDIO DEVICES"]
        XCTAssertTrue(audioDevices.exists, "AUDIO DEVICES button should exist")
    }
}
