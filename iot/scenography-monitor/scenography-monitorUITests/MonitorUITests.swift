//
//  MonitorUITests.swift
//  scenography-monitorUITests
//
//  Created by Antigravity on 06/01/2026.
//

import XCTest

final class MonitorUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    // MARK: - Network Inspector Tests
    
    func testNetworkInspectorOpening() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Open Network Inspector
        let netCheckButton = app.buttons["NET CHECK"]
        XCTAssertTrue(netCheckButton.waitForExistence(timeout: 2), "NET CHECK button should exist")
        
        netCheckButton.click()
        
        // Verify inspector elements
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2), "NETWORK CONFIG title should appear")
        XCTAssertTrue(app.staticTexts["WebSocket URL"].exists, "WebSocket URL label should exist")
        XCTAssertTrue(app.textFields["websocket_url_field"].exists, "URL text field should exist")
        XCTAssertTrue(app.buttons["reset_url_button"].exists, "Reset URL button should exist")
    }
    
    func testWebSocketUrlEditing() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Open Network Inspector
        app.buttons["NET CHECK"].click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2))
        
        // Get URL field
        let urlField = app.textFields["websocket_url_field"]
        XCTAssertTrue(urlField.exists, "URL field should exist")
        
        // Clear and type new URL
        urlField.click()
        urlField.typeKey("a", modifierFlags: .command) // Select all
        urlField.typeText("ws://test.local/ws")
        
        // Verify new value
        XCTAssertEqual(urlField.value as? String, "ws://test.local/ws", "URL should be updated")
    }
    
    func testResetUrlButton() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Open Network Inspector
        app.buttons["NET CHECK"].click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2))
        
        let urlField = app.textFields["websocket_url_field"]
        let resetButton = app.buttons["reset_url_button"]
        
        // Change URL
        urlField.click()
        urlField.typeKey("a", modifierFlags: .command)
        urlField.typeText("ws://changed.url/ws")
        
        // Reset to default
        resetButton.click()
        
        // Verify default URL is restored
        let defaultUrl = "ws://192.168.10.7:8000/ws"
        XCTAssertEqual(urlField.value as? String, defaultUrl, "URL should be reset to default")
    }
    
    func testConnectionStatusDisplay() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Open Network Inspector
        app.buttons["NET CHECK"].click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2))
        
        // Check connection status elements exist
        XCTAssertTrue(app.otherElements["connection_indicator"].exists || app.images["connection_indicator"].exists || app.staticTexts["connection_status_label"].exists, "Connection indicator or status should exist")
        
        // Connect button should exist
        let connectButton = app.buttons["connect_button"]
        XCTAssertTrue(connectButton.exists, "Connect/Disconnect button should exist")
    }
    
    func testConnectDisconnectButton() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Open Network Inspector
        app.buttons["NET CHECK"].click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2))
        
        let connectButton = app.buttons["connect_button"]
        XCTAssertTrue(connectButton.exists)
        
        // Click connect/disconnect
        connectButton.click()
        
        // Wait a moment for state change
        Thread.sleep(forTimeInterval: 0.5)
        
        // Button should still exist (state may have changed)
        XCTAssertTrue(connectButton.exists, "Connect button should still exist after click")
    }
    
    // MARK: - Logs Section Tests
    
    func testLogsSection() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Open Network Inspector
        app.buttons["NET CHECK"].click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2))
        
        // Verify logs section exists
        XCTAssertTrue(app.staticTexts["Recent Logs"].exists, "Recent Logs label should exist")
    }
    
    // MARK: - Inspector Toggle Tests
    
    func testInspectorToggle() throws {
        let app = XCUIApplication()
        app.launch()
        
        let netCheckButton = app.buttons["NET CHECK"]
        
        // Initially closed
        XCTAssertFalse(app.staticTexts["NETWORK CONFIG"].exists)
        
        // Open
        netCheckButton.click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2))
        
        // Close
        netCheckButton.click()
        
        // Wait for animation
        Thread.sleep(forTimeInterval: 0.3)
        XCTAssertFalse(app.staticTexts["NETWORK CONFIG"].exists)
        
        // Reopen
        netCheckButton.click()
        XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2))
    }
}
