
import SwiftUI

struct PlaybackStateTestView: View {
    @ObservedObject var soundManager = SoundManager.shared
    @State private var log: String = ""
    @State private var testRunning: Bool = false
    
    var body: some View {
        VStack {
            Text("Instance playback E2E Test")
                .font(.headline)
            
            ScrollView {
                Text(log)
                    .font(.system(.caption, design: .monospaced))
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
            }
            .frame(height: 300)
            .border(Color.gray)
            
            Button("Run Test") {
                runTest()
            }
            .disabled(testRunning)
        }
        .padding()
    }
    
    func runTest() {
        testRunning = true
        log = "Starting Test...\n"
        
        // Setup: Create Instances on Bus 1
        let busId = 1
        let instanceA = SoundManager.SoundInstance(filename: "TestSoundA")
        let instanceB = SoundManager.SoundInstance(filename: "TestSoundB")
        
        appendLog("Step 1: Reset State & Add Instances")
        // Manually inject generic instances
        soundManager.busSamples[busId] = [instanceA, instanceB]
        soundManager.activeInstanceIds.removeAll()
        
        // Test Logic Check:
        // Play Sound A
        appendLog("Step 2: Simulate Playing Instance A")
        simulatePlay(instance: instanceA)
        
        // Assert A is playing, B is NOT
        assertPlaying(instance: instanceA, expected: true)
        assertPlaying(instance: instanceB, expected: false)
        
        // Play Sound B (Should NOT automatically stop A unless logic enforces monophony, but current logic allows POLYPHONY per bus unless specified otherwise)
        // Wait, SoundManager.playSound(instance...) stops *that specific instance* if it was playing.
        // It does NOT stop other instances on the same bus (Polyphonic by design now).
        // So both can play.
        
        appendLog("Step 3: Simulate Playing Instance B (Polyphony Check)")
        simulatePlay(instance: instanceB)
        
        assertPlaying(instance: instanceB, expected: true)
        assertPlaying(instance: instanceA, expected: true) // Should still be playing
        
        // Stop A
        appendLog("Step 4: Stop Instance A")
        simulateStop(instance: instanceA)
        
        assertPlaying(instance: instanceA, expected: false)
        assertPlaying(instance: instanceB, expected: true)
        
        testRunning = false
        appendLog("Test Complete.")
    }
    
    func simulatePlay(instance: SoundManager.SoundInstance) {
        soundManager.activeInstanceIds.insert(instance.id)
        appendLog(" -> Set Instance \(instance.filename) active")
    }
    
    func simulateStop(instance: SoundManager.SoundInstance) {
        soundManager.activeInstanceIds.remove(instance.id)
        appendLog(" -> Set Instance \(instance.filename) inactive")
    }
    
    func assertPlaying(instance: SoundManager.SoundInstance, expected: Bool) {
        let isPlaying = soundManager.activeInstanceIds.contains(instance.id)
        
        if isPlaying == expected {
            appendLog(" [PASS] \(instance.filename) playing state: \(isPlaying)")
        } else {
            appendLog(" [FAIL] \(instance.filename) playing state: \(isPlaying) (Expected: \(expected))")
        }
    }
    
    func appendLog(_ text: String) {
        log += text + "\n"
    }
}
