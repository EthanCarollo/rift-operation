//
//  pinguinUITests.swift
//  pinguinUITests
//
//  Created by eth on 17/12/2025.
//

import XCTest

final class pinguinUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    override func tearDownWithError() throws {
    }

    @MainActor
    func testLaunchPerformance() throws {
        measure(metrics: [XCTApplicationLaunchMetric()]) {
            XCUIApplication().launch()
        }
    }
    
    // MARK: - Server Selection Screen Tests
    
    @MainActor
    func testServerSelectionScreenShowsOnLaunch() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Verify server selection buttons are visible
        let cosmoCard = app.buttons["cosmoCard"]
        let darkCosmoCard = app.buttons["darkCosmoCard"]
        
        XCTAssertTrue(cosmoCard.waitForExistence(timeout: 5), "Cosmo card should exist on launch")
        XCTAssertTrue(darkCosmoCard.waitForExistence(timeout: 5), "Dark Cosmo card should exist on launch")
    }
    
    @MainActor
    func testSelectCosmoNavigatesToContentView() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Tap Cosmo card
        let cosmoCard = app.buttons["cosmoCard"]
        XCTAssertTrue(cosmoCard.waitForExistence(timeout: 5))
        cosmoCard.tap()
        
        // Verify we're on ContentView (status indicator should be visible)
        let statusIndicator = app.otherElements["statusIndicator"]
        XCTAssertTrue(statusIndicator.waitForExistence(timeout: 5), "Should navigate to ContentView after selecting Cosmo")
    }
    
    @MainActor
    func testSelectDarkCosmoNavigatesToContentView() throws {
        let app = XCUIApplication()
        app.launch()
        
        // Tap Dark Cosmo card
        let darkCosmoCard = app.buttons["darkCosmoCard"]
        XCTAssertTrue(darkCosmoCard.waitForExistence(timeout: 5))
        darkCosmoCard.tap()
        
        // Verify we're on ContentView (status indicator should be visible)
        let statusIndicator = app.otherElements["statusIndicator"]
        XCTAssertTrue(statusIndicator.waitForExistence(timeout: 5), "Should navigate to ContentView after selecting Dark Cosmo")
    }
    
    // MARK: - ContentView Tests (after server selection)
    
    private func launchAndSelectCosmo() -> XCUIApplication {
        let app = XCUIApplication()
        app.launch()
        let cosmoCard = app.buttons["cosmoCard"]
        if cosmoCard.waitForExistence(timeout: 3) {
            cosmoCard.tap()
        }
        return app
    }
    
    @MainActor
    func testStatusIndicatorExists() throws {
        let app = launchAndSelectCosmo()
        
        // Verify status indicator is visible
        let statusIndicator = app.otherElements["statusIndicator"]
        XCTAssertTrue(statusIndicator.waitForExistence(timeout: 5), "Status indicator should exist")
        
        // Verify status label exists
        let statusLabel = app.staticTexts["statusLabel"]
        XCTAssertTrue(statusLabel.waitForExistence(timeout: 5), "Status label should exist")
    }
    
    @MainActor
    func testServerModePickerExists() throws {
        let app = launchAndSelectCosmo()
        
        // Verify server mode picker is visible
        let serverModePicker = app.buttons["serverModePicker"]
        XCTAssertTrue(serverModePicker.waitForExistence(timeout: 5), "Server mode picker should exist")
    }
    
    @MainActor
    func testServerModePickerShowsOptions() throws {
        let app = launchAndSelectCosmo()
        
        // Tap the server mode picker to open menu
        let serverModePicker = app.buttons["serverModePicker"]
        XCTAssertTrue(serverModePicker.waitForExistence(timeout: 5))
        serverModePicker.tap()
        
        // Verify both modes appear in the menu
        let cosmoOption = app.buttons["Cosmo"]
        let darkCosmoOption = app.buttons["Dark Cosmo"]
        
        XCTAssertTrue(cosmoOption.waitForExistence(timeout: 3), "Cosmo option should appear in menu")
        XCTAssertTrue(darkCosmoOption.waitForExistence(timeout: 3), "Dark Cosmo option should appear in menu")
    }
    
    @MainActor
    func testUIElementsVisibleAfterServerSelection() throws {
        let app = launchAndSelectCosmo()
        
        // Test core UI elements exist
        let statusIndicator = app.otherElements["statusIndicator"]
        let statusLabel = app.staticTexts["statusLabel"]
        let serverModePicker = app.buttons["serverModePicker"]
        
        XCTAssertTrue(statusIndicator.waitForExistence(timeout: 5), "Status indicator should be visible")
        XCTAssertTrue(statusLabel.waitForExistence(timeout: 5), "Status label should be visible")
        XCTAssertTrue(serverModePicker.waitForExistence(timeout: 5), "Server mode picker should be visible")
    }
}


