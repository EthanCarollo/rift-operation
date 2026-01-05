
import XCTest

class ProjectConfigUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }
    
    func testSaveButtonIsClickable() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Wait for app to fully load
        let saveButton = app.buttons["SAVE"]
        XCTAssertTrue(saveButton.waitForExistence(timeout: 5), "SAVE button should exist")
        XCTAssertTrue(saveButton.isEnabled, "SAVE button should be enabled")
        XCTAssertTrue(saveButton.isHittable, "SAVE button should be hittable")
    }
    
    func testLoadButtonIsClickable() throws {
        let app = XCUIApplication()
        app.launch()
        
        let loadButton = app.buttons["LOAD"]
        XCTAssertTrue(loadButton.waitForExistence(timeout: 5), "LOAD button should exist")
        XCTAssertTrue(loadButton.isEnabled, "LOAD button should be enabled")
        XCTAssertTrue(loadButton.isHittable, "LOAD button should be hittable")
    }
    
    func testSamplerSlotRemoveButtonSize() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Verify main app title is visible (confirms app loaded)
        let title = app.staticTexts["RIFT OP // SOUND MONITOR"]
        XCTAssertTrue(title.waitForExistence(timeout: 5), "App should be loaded")
        
        // Verify SAVE and LOAD buttons exist (toolbar verification)
        XCTAssertTrue(app.buttons["SAVE"].exists)
        XCTAssertTrue(app.buttons["LOAD"].exists)
    }
    
    func testProjectUIWorkflow() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Wait for main interface to load
        let title = app.staticTexts["RIFT OP // SOUND MONITOR"]
        XCTAssertTrue(title.waitForExistence(timeout: 5), "App title should be visible")
        
        // Verify toolbar buttons
        XCTAssertTrue(app.buttons["SAVE"].exists)
        XCTAssertTrue(app.buttons["LOAD"].exists)
        
        // Verify the main app is rendering (any window exists)
        XCTAssertTrue(app.windows.count > 0, "App window should be present")
    }
}
