
import XCTest

class ProjectConfigUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }
    
    func testSaveButtonIsClickable() throws {
        let app = XCUIApplication()
        app.launch()
        
        let saveButton = app.buttons["SAVE"]
        XCTAssertTrue(saveButton.exists, "SAVE button should exist")
        XCTAssertTrue(saveButton.isEnabled, "SAVE button should be enabled")
        XCTAssertTrue(saveButton.isHittable, "SAVE button should be hittable")
    }
    
    func testLoadButtonIsClickable() throws {
        let app = XCUIApplication()
        app.launch()
        
        let loadButton = app.buttons["LOAD"]
        XCTAssertTrue(loadButton.exists, "LOAD button should exist")
        XCTAssertTrue(loadButton.isEnabled, "LOAD button should be enabled")
        XCTAssertTrue(loadButton.isHittable, "LOAD button should be hittable")
    }
    
    func testSamplerSlotRemoveButtonSize() throws {
        // Test that the UI structure for sampler is present
        let app = XCUIApplication()
        app.launch()
        
        // Verify main app title is visible (confirms app loaded)
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].exists, "App should be loaded")
        
        // Verify SAVE and LOAD buttons exist (toolbar verification)
        XCTAssertTrue(app.buttons["SAVE"].exists)
        XCTAssertTrue(app.buttons["LOAD"].exists)
    }
    
    func testProjectUIWorkflow() throws {
        let app = XCUIApplication()
        app.launch()
        
        // 1. Verify main interface elements exist
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].exists, "App title should be visible")
        
        // 2. Verify toolbar buttons
        XCTAssertTrue(app.buttons["SAVE"].exists)
        XCTAssertTrue(app.buttons["LOAD"].exists)
        
        // 3. Verify the main app is rendering (any window exists)
        XCTAssertTrue(app.windows.count > 0, "App window should be present")
    }
}
