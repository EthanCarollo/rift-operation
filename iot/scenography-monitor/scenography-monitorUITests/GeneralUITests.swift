//
//  GeneralUITests.swift
//  scenography-monitorUITests
//
//  Created by Antigravity on 22/12/2025.
//

import XCTest

final class GeneralUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testAppNavigation() throws {
        let app = XCUIApplication()
        app.launch()
        
        // 1. Verify Title Exists
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].exists, "App title missing")
        
        // 2. Toggle Network Inspector
        let netCheckButton = app.buttons["NET CHECK"]
        XCTAssertTrue(netCheckButton.exists, "NET CHECK button missing")
        
        netCheckButton.click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].exists, "Inspector did not appear")
        
        // Close Inspector
        netCheckButton.click()
        XCTAssertFalse(app.staticTexts["NETWORK CONFIG"].exists, "Inspector did not disappear")
        
        // 3. Toggle Output List
        // The button has image "sidebar.right". 
        // We find it by image name since it has no text.
        let sidebarButton = app.buttons.containing(NSPredicate(format: "image.name == 'sidebar.right'")).firstMatch
        XCTAssertTrue(sidebarButton.exists, "Sidebar toggle button missing")
        
        // Default is TRUE (Visible).
        XCTAssertTrue(app.staticTexts["SYSTEM AUDIO DEVICES"].exists, "Output list should be visible by default")
        
        // Hide
        sidebarButton.click()
        XCTAssertFalse(app.staticTexts["SYSTEM AUDIO DEVICES"].exists, "Output list did not hide")
        
        // Show
        sidebarButton.click()
        XCTAssertTrue(app.staticTexts["SYSTEM AUDIO DEVICES"].exists, "Output list did not show")
    }
    
    func testBusControls() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Check for presence of at least one Bus view
        // Bus 1 is named "SAS" by default
        let sasBus = app.textFields["SAS"] // It's an editable text field
        // Or static text "BUS 1" above it
        XCTAssertTrue(app.staticTexts["BUS 1"].exists)
        
        // Metadata fields should be editable
        if sasBus.exists {
            sasBus.click()
            sasBus.typeText(" TEST")
            // Verify content changed (UI Test allows this)
            XCTAssertEqual(sasBus.value as? String, "SAS TEST")
        }
        
        // Mute/Solo
        // Using first match for "M" and "S" buttons
        let muteButton = app.buttons["M"].firstMatch
        let soloButton = app.buttons["S"].firstMatch
        
        XCTAssertTrue(muteButton.exists)
        XCTAssertTrue(soloButton.exists)
        
        muteButton.click()
        soloButton.click()
    }
    
    func testFilterPicker() throws {
        let app = XCUIApplication()
        app.launch()
        
        // The picker shows "ALL" initially (-1 tag)
        let filterPicker = app.popUpButtons.firstMatch
        // If not popUpButton, try finding by text "ALL"
        
        if filterPicker.exists {
             filterPicker.click()
             // Verify "Unassigned" option exists
             XCTAssertTrue(app.menuItems["Unassigned"].exists)
             // Verify "SAS" option exists
             XCTAssertTrue(app.menuItems["SAS"].exists)
        }
    }
}
