
import XCTest

class SamplerUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testSamplerLayout() throws {
        let app = XCUIApplication()
        app.launch()
        
        // 1. Verify we are in Sampler View
        // Bus Tracks should be visible (e.g., "BUS 1", "BUS 2")
        // Note: Default bus names are "BUS 1", "BUS 2"...
        // Our custom UI renders them.
        
        let bus1StaticText = app.staticTexts["BUS 1"]
        XCTAssertTrue(bus1StaticText.exists, "BUS 1 track should be visible")
        
        // 2. Verify Save/Load buttons (Top Bar)
        XCTAssertTrue(app.buttons["SAVE"].exists)
        XCTAssertTrue(app.buttons["LOAD"].exists)
        
        // 3. Verify Library is present (Header "SOUND LIBRARY")
        XCTAssertTrue(app.staticTexts["SOUND LIBRARY"].exists)
    }
    
    // Note: True Drag & Drop automation in XCTest is tricky/flaky without accessibility identifiers setup for drop targets.
    // For now, we verify the layout structure supports the workflow.
}
