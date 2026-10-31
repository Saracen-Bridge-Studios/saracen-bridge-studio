import XCTest

/// Runs on GitHub's Macs in the iPhone simulator, against a Studio hosting a test production on the same Mac. Every
/// step is kept as a screenshot in the test results (the workflow exports them as PNGs for Tim).
///
/// ROOM_TEST_INVITE: an invite link from that Studio (the workflow sets it, and approves the phone when its safety
/// words come up, as an executive would).
final class ScreenshotTests: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["-uitestReset"]
    }

    func shot(_ name: String) {
        let a = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        a.name = name
        a.lifetime = .keepAlways
        add(a)
    }

    func testTheAppEndToEnd() throws {
        let invite = ProcessInfo.processInfo.environment["ROOM_TEST_INVITE"] ?? ""
        app.launch()
        XCTAssertTrue(app.buttons["join-invite"].waitForExistence(timeout: 10))
        shot("01 Welcome")

        app.buttons["join-invite"].tap()
        let field = app.textViews["invite-field"].exists ? app.textViews["invite-field"] : app.textFields["invite-field"]
        XCTAssertTrue(field.waitForExistence(timeout: 5))
        shot("02 Join a Room")
        try XCTSkipIf(invite.isEmpty, "No test Studio: ROOM_TEST_INVITE isn't set")
        field.tap()
        field.typeText(invite)
        app.buttons["join-submit"].tap()

        // the Room page, through the relay
        let web = app.webViews.firstMatch
        XCTAssertTrue(web.waitForExistence(timeout: 20))
        let name = web.textFields.firstMatch
        XCTAssertTrue(name.waitForExistence(timeout: 20), "the join screen didn't load through the relay")
        shot("03 Join the Room")
        name.tap()
        name.typeText("UI Test Phone")
        web.buttons["Join"].tap()

        XCTAssertTrue(web.staticTexts["Your safety words"].waitForExistence(timeout: 60), "no safety words: the phone wasn't checked")
        shot("04 Safety words")
        XCTAssertTrue(web.buttons["Open the Room"].waitForExistence(timeout: 60), "not approved")
        shot("05 You're in")
        web.buttons["Open the Room"].tap()
        sleep(3)
        shot("06 Today")
        for (tab, n) in [("Board", "07"), ("Chat", "08"), ("Meet", "09")] {
            web.buttons[tab].tap()
            sleep(2)
            shot("\(n) \(tab)")
        }

        app.navigationBars.buttons.element(boundBy: 0).tap()
        XCTAssertTrue(app.staticTexts["Your Studios"].waitForExistence(timeout: 5) || app.cells.count > 0)
        shot("10 Your Studios")
        app.buttons["Settings"].tap()
        sleep(1)
        shot("11 Settings")
    }
}
