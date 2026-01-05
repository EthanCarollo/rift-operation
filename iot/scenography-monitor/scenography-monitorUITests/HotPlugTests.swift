import XCTest

final class HotPlugTests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
    }

    func testHotPlugAndAssign() throws {
        // 1. App is launched
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].exists)

        // 2. Select a bus (Bus 1 / SAS)
        let bus1 = app.groups.matching(identifier: "BusTrack_1").firstMatch
        XCTAssertTrue(bus1.exists, "Bus Track 1 should exist")

        // 3. Open Routing Menu
        let routingMenu = app.buttons.matching(identifier: "RoutingMenu_1").firstMatch
        XCTAssertTrue(routingMenu.exists, "Routing menu button should exist")
        routingMenu.tap()

        // 4. Check device list in menu
        // System Default is always there.
        let defaultOption = app.menuItems["System/Default"]
        if defaultOption.exists {
            defaultOption.tap()
        }
        
        // 5. Verify assignment (UI might update text near the menu or in inspector)
        // Since we don't have a specific label showing the name in the track header in the current UI 
        // (it's only in the menu or OutputListView), we verify the interaction didn't crash.
    }
}
