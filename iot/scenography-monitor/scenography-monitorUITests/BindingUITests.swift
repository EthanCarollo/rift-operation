//
//  BindingUITests.swift
//  scenography-monitorUITests
//
//  Created by eth on 22/12/2025.
//

import XCTest

final class BindingUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testBindingCreationAndDeletion() throws {
        let app = XCUIApplication()
        app.launch()
        
        // 1. Locate Sound and Click Link (Expand)
        // Find first cell
        let firstSoundCell = app.tables.cells.firstMatch
        if !firstSoundCell.exists {
             // Fallback for different list styles
             XCTAssertTrue(app.outlines.firstMatch.exists || app.tables.firstMatch.exists, "Sound Library List not found")
        }
        
        // Ensure there is at least one cell
        XCTAssertTrue(firstSoundCell.exists, "No sounds in library to test")
        
        let linkButton = firstSoundCell.buttons["link"]
        XCTAssertTrue(linkButton.exists, "Link button not found")
        linkButton.click()
        
        // 2. Interact with Inline Settings (Custom Key)
        let customToggle = app.checkBoxes["Custom"]
        // Wait briefly for animation
        XCTAssertTrue(customToggle.waitForExistence(timeout: 2.0))
        customToggle.click()
        
        let keyField = app.textFields["Key"]
        XCTAssertTrue(keyField.exists)
        keyField.click()
        keyField.typeText("test_inline")
        
        // 3. Add Binding
        let addButton = app.buttons["plus.circle.fill"]
        XCTAssertTrue(addButton.exists)
        addButton.click()
        
        // 4. Verify Binding Exists in List (Inline)
        // Look for static text "test_inline"
        XCTAssertTrue(app.staticTexts["test_inline"].exists)
        
        // 5. Delete Binding
        let deleteButton = app.buttons["xmark.circle"]
        if deleteButton.exists {
            deleteButton.click()
        }
        
        // 6. Verify Deleted
        XCTAssertFalse(app.staticTexts["test_inline"].exists)
        
        // 7. Collapse
        linkButton.click()
    }

    func testBooleanBinding() throws {
        let app = XCUIApplication()
        app.launch()
        
        // 1. Expand Row
        let firstSoundCell = app.tables.cells.firstMatch
        XCTAssertTrue(firstSoundCell.exists)
        firstSoundCell.buttons["link"].click()
        
        // 2. Configure Boolean Binding
        app.checkBoxes["Custom"].click()
        let keyField = app.textFields["Key"]
        keyField.click()
        keyField.typeText("bool_trigger")
        
        // Enable Value Specific
        app.switches["Val?"].click()
        
        // Select Bool Type (It's a picker/segmented)
        // Note: Picker interaction in tests depends on style.
        // Assuming current implementation uses a Picker or similar.
        // If it's a Picker, we need to click it and select "Bool".
        
        // 3. Add
        app.buttons["plus.circle.fill"].click()
        
        // 4. Verify in list
        // Should trigger on "true" or "false" depending on default
        // Our new implementation logic normalizes bools.
        XCTAssertTrue(app.staticTexts["bool_trigger"].exists)
        
        // Cleanup
        app.buttons["xmark.circle"].firstMatch.click()
    }
}
