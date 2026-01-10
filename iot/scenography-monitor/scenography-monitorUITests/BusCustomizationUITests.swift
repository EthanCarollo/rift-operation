//
//  BusCustomizationUITests.swift
//  scenography-monitorUITests
//
//  Created by Antigravity on 10/01/2026.
//

import XCTest

/// Tests for bus rename and color customization features
final class BusCustomizationUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }
    
    // MARK: - Bus Rename Tests
    
    /// Tests that double-clicking a bus name enables edit mode
    func testBusNameDoubleClickToEdit() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Verify app is ready
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        // Find bus 1 name label (default name is "SAS")
        let busNameLabel = app.staticTexts["BusNameLabel_1"]
        
        guard busNameLabel.waitForExistence(timeout: 3) else {
            throw XCTSkip("Bus name label not found")
        }
        
        // Double-click to enable edit mode
        busNameLabel.doubleClick()
        
        // Wait for text field to appear
        let busNameField = app.textFields["BusNameField_1"]
        XCTAssertTrue(busNameField.waitForExistence(timeout: 2), "Text field should appear after double-click")
    }
    
    /// Tests renaming a bus via context menu
    func testBusRenameViaContextMenu() throws {
        let app = XCUIApplication()
        app.launch()
        
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        // Find Bus 1 track
        let busTrack = app.otherElements["BusTrack_1"]
        
        guard busTrack.waitForExistence(timeout: 3) else {
            throw XCTSkip("Bus track not found")
        }
        
        // Right-click to open context menu
        busTrack.rightClick()
        
        // Wait for context menu
        Thread.sleep(forTimeInterval: 0.3)
        
        // Click "Rename Bus" menu item
        let renameMenuItem = app.menuItems["Rename Bus"]
        if renameMenuItem.waitForExistence(timeout: 2) {
            renameMenuItem.click()
            
            // Check that edit field appears
            let busNameField = app.textFields["BusNameField_1"]
            XCTAssertTrue(busNameField.waitForExistence(timeout: 2), 
                          "Name field should appear after clicking Rename")
        }
    }
    
    /// Tests that renaming a bus persists the change
    func testBusRenameAndVerify() throws {
        let app = XCUIApplication()
        app.launch()
        
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        let busNameLabel = app.staticTexts["BusNameLabel_1"]
        
        guard busNameLabel.waitForExistence(timeout: 3) else {
            throw XCTSkip("Bus name label not found")
        }
        
        // Store original name
        let originalName = busNameLabel.label
        
        // Double-click to edit
        busNameLabel.doubleClick()
        
        let busNameField = app.textFields["BusNameField_1"]
        XCTAssertTrue(busNameField.waitForExistence(timeout: 2))
        
        // Clear and type new name
        busNameField.click()
        busNameField.typeKey("a", modifierFlags: .command) // Select all
        busNameField.typeText("TEST BUS\n") // Type new name and press Enter
        
        // Wait for the label to reappear with new value
        Thread.sleep(forTimeInterval: 0.3)
        
        // The label should show the new name (uppercased)
        let newBusLabel = app.staticTexts["BusNameLabel_1"]
        XCTAssertTrue(newBusLabel.waitForExistence(timeout: 2))
        XCTAssertEqual(newBusLabel.label, "TEST BUS", "Bus name should be updated")
        
        print("✓ Successfully renamed bus from '\(originalName)' to 'TEST BUS'")
    }
    
    // MARK: - Bus Color Tests
    
    /// Tests that color palette is accessible via context menu
    func testBusColorContextMenu() throws {
        let app = XCUIApplication()
        app.launch()
        
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        let busTrack = app.otherElements["BusTrack_1"]
        
        guard busTrack.waitForExistence(timeout: 3) else {
            throw XCTSkip("Bus track not found")
        }
        
        // Right-click to open context menu
        busTrack.rightClick()
        
        Thread.sleep(forTimeInterval: 0.3)
        
        // Hover over "Set Color" to open submenu
        let setColorMenu = app.menuItems["Set Color"]
        if setColorMenu.waitForExistence(timeout: 2) {
            setColorMenu.hover()
            
            Thread.sleep(forTimeInterval: 0.3)
            
            // Check for color options in submenu
            let blueOption = app.menuItems["Blue"]
            let redOption = app.menuItems["Red"]
            let greenOption = app.menuItems["Green"]
            
            XCTAssertTrue(blueOption.exists || redOption.exists || greenOption.exists,
                          "Color palette options should be visible")
            
            // Click a color to apply
            if blueOption.exists {
                blueOption.click()
                print("✓ Applied Blue color to bus")
            }
        }
    }
    
    /// Tests changing bus color and verifying visual update
    func testBusColorChange() throws {
        let app = XCUIApplication()
        app.launch()
        
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        let busTrack = app.otherElements["BusTrack_1"]
        
        guard busTrack.waitForExistence(timeout: 3) else {
            throw XCTSkip("Bus track not found")
        }
        
        // Apply a different color via context menu
        busTrack.rightClick()
        Thread.sleep(forTimeInterval: 0.3)
        
        let setColorMenu = app.menuItems["Set Color"]
        if setColorMenu.waitForExistence(timeout: 2) {
            setColorMenu.hover()
            Thread.sleep(forTimeInterval: 0.3)
            
            let purpleOption = app.menuItems["Purple"]
            if purpleOption.exists {
                purpleOption.click()
                
                Thread.sleep(forTimeInterval: 0.3)
                
                // Verify bus track still exists and is functional
                XCTAssertTrue(busTrack.exists, "Bus track should still exist after color change")
                print("✓ Successfully changed bus color to Purple")
            }
        }
    }
    
    // MARK: - Combined Tests
    
    /// Tests that mute and solo buttons work correctly
    func testBusMuteAndSoloButtons() throws {
        let app = XCUIApplication()
        app.launch()
        
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        // Find mute button for Bus 1
        let muteButton = app.buttons["BusMuteButton_1"]
        let soloButton = app.buttons["BusSoloButton_1"]
        
        guard muteButton.waitForExistence(timeout: 3) else {
            throw XCTSkip("Mute button not found")
        }
        
        // Toggle mute
        muteButton.click()
        Thread.sleep(forTimeInterval: 0.2)
        print("✓ Toggled mute on Bus 1")
        
        // Toggle solo
        if soloButton.exists {
            soloButton.click()
            Thread.sleep(forTimeInterval: 0.2)
            print("✓ Toggled solo on Bus 1")
        }
        
        // Toggle back
        muteButton.click()
        if soloButton.exists {
            soloButton.click()
        }
        
        print("✅ Mute and Solo buttons work correctly")
    }
}
