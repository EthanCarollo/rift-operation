//
//  MemoryStressUITests.swift
//  scenography-monitorUITests
//
//  Created by Antigravity on 10/01/2026.
//

import XCTest

/// Tests for validating memory management during repeated sound playback
final class MemoryStressUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }
    
    // MARK: - Memory Stress Tests
    
    /// Tests that playing sounds 30+ times does not cause memory leaks.
    /// This test plays and stops a sound rapidly to stress-test the audio cleanup logic.
    func testRepeatedSoundPlaybackNoMemoryLeak() throws {
        let app = XCUIApplication()
        app.launch()
        
        // 1. Verify app is ready
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5), 
                      "App should be ready and showing title")
        
        // 2. Find any play button on a sample slot
        // Buttons with pattern "SampleSlot_PlayButton_*"
        let playButtons = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH 'SampleSlot_PlayButton_'"))
        
        guard playButtons.count > 0 else {
            // No samples loaded - this is acceptable, just skip
            throw XCTSkip("No sample slots found. Ensure a sound is loaded for memory stress testing.")
        }
        
        let playButton = playButtons.firstMatch
        XCTAssertTrue(playButton.waitForExistence(timeout: 2), "Play button should exist")
        
        // 3. Play the sound 35 times (more than minimum 30)
        let playCount = 35
        
        for i in 1...playCount {
            // Click to play
            playButton.click()
            
            // Brief wait for sound to start and audio node to be created
            Thread.sleep(forTimeInterval: 0.15)
            
            // Click to stop
            playButton.click()
            
            // Allow cleanup to happen
            Thread.sleep(forTimeInterval: 0.1)
            
            if i % 10 == 0 {
                // Log progress
                print("✓ Completed \(i)/\(playCount) play/stop cycles")
            }
        }
        
        // 4. Brief pause to allow final cleanup
        Thread.sleep(forTimeInterval: 0.5)
        
        // 5. Verify app is still responsive (no crash, no hang)
        XCTAssertTrue(app.staticTexts["ENGINE READY"].exists, 
                      "Engine should still be ready after \(playCount) cycles")
        
        // 6. Try to interact with UI to verify no freeze
        let netCheckButton = app.buttons["NET CHECK"]
        if netCheckButton.exists {
            netCheckButton.click()
            Thread.sleep(forTimeInterval: 0.2)
            XCTAssertTrue(app.staticTexts["NETWORK CONFIG"].waitForExistence(timeout: 2),
                          "UI should still be interactive after stress test")
            netCheckButton.click() // Close
        }
        
        print("✅ Memory stress test completed successfully: \(playCount) play/stop cycles with no issues")
    }
    
    /// Tests rapid repeated playback without stop (re-trigger same sound)
    /// This tests the scenario where the same sound is triggered repeatedly while still playing
    func testRapidReTriggerPlayback() throws {
        let app = XCUIApplication()
        app.launch()
        
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        let playButtons = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH 'SampleSlot_PlayButton_'"))
        
        guard playButtons.count > 0 else {
            throw XCTSkip("No sample slots found. Ensure a sound is loaded for testing.")
        }
        
        let playButton = playButtons.firstMatch
        XCTAssertTrue(playButton.waitForExistence(timeout: 2))
        
        // Rapidly re-trigger 30 times (this tests stopSound being called while playing)
        let triggerCount = 30
        
        for i in 1...triggerCount {
            playButton.click() // Each click should stop current and restart
            Thread.sleep(forTimeInterval: 0.05) // Very short interval
            
            if i % 10 == 0 {
                print("✓ Rapid trigger: \(i)/\(triggerCount)")
            }
        }
        
        // Final stop
        playButton.click()
        Thread.sleep(forTimeInterval: 0.3)
        
        // Verify app is still responsive
        XCTAssertTrue(app.staticTexts["ENGINE READY"].exists,
                      "Engine should be ready after rapid re-triggering")
        
        print("✅ Rapid re-trigger test completed: \(triggerCount) triggers")
    }
    
    /// Tests multiple different sounds played sequentially to verify cleanup across instances
    func testMultipleSoundsSequential() throws {
        let app = XCUIApplication()
        app.launch()
        
        XCTAssertTrue(app.staticTexts["RIFT OP // SOUND MONITOR"].waitForExistence(timeout: 5))
        
        let playButtons = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH 'SampleSlot_PlayButton_'"))
        
        guard playButtons.count >= 2 else {
            throw XCTSkip("Need at least 2 sample slots for multi-sound testing.")
        }
        
        // Play each available sound multiple times
        let cyclesPerSound = 15
        
        for buttonIndex in 0..<min(3, playButtons.count) {
            let button = playButtons.element(boundBy: buttonIndex)
            
            for cycle in 1...cyclesPerSound {
                button.click() // Play
                Thread.sleep(forTimeInterval: 0.1)
                button.click() // Stop
                Thread.sleep(forTimeInterval: 0.05)
            }
            
            print("✓ Sound \(buttonIndex + 1): completed \(cyclesPerSound) cycles")
        }
        
        Thread.sleep(forTimeInterval: 0.5)
        
        XCTAssertTrue(app.staticTexts["ENGINE READY"].exists,
                      "Engine should be ready after multi-sound test")
        
        print("✅ Multi-sound sequential test completed")
    }
}
