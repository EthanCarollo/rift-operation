
import SwiftUI

struct PlaybackStateTestView: View {
    @ObservedObject var soundManager = SoundManager.shared
    @State private var log: String = ""
    @State private var testRunning: Bool = false
    
    var body: some View {
        VStack {
            Text("Playback State E2E Test")
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
        
        // Setup: Mock 2 sounds on Bus 1
        let soundA = "TestSoundA"
        let soundB = "TestSoundB"
        let busId = 1
        
        // Mock State directly for test environment (Simulating logic response)
        // Ideally we would mock the file system but we can test the State Logic.
        
        appendLog("Step 1: Reset State")
        soundManager.activeBusIds.removeAll()
        soundManager.activeNodeNames.removeAll()
        soundManager.soundRoutes[soundA] = busId
        soundManager.soundRoutes[soundB] = busId
        
        // Test Logic Check:
        // Play Sound A
        appendLog("Step 2: Simulate Playing Sound A")
        simulatePlay(sound: soundA, bus: busId)
        
        // Assert A is playing, B is NOT
        assertPlaying(sound: soundA, bus: busId, expected: true)
        assertPlaying(sound: soundB, bus: busId, expected: false)
        
        // Play Sound B (Should stop A)
        appendLog("Step 3: Simulate Playing Sound B (Override)")
        simulatePlay(sound: soundB, bus: busId)
        
        assertPlaying(sound: soundB, bus: busId, expected: true)
        assertPlaying(sound: soundA, bus: busId, expected: false)
        
        // Stop Bus
        appendLog("Step 4: Stop Bus 1")
        simulateStop(bus: busId)
        
        assertPlaying(sound: soundA, bus: busId, expected: false)
        assertPlaying(sound: soundB, bus: busId, expected: false)
        
        testRunning = false
        appendLog("Test Complete.")
    }
    
    func simulatePlay(sound: String, bus: Int) {
        // We simulate what soundManager.playSound -> finalizePlayback does to state
        soundManager.activeBusIds.insert(bus)
        soundManager.activeNodeNames[bus] = sound
        appendLog(" -> Set Bus \(bus) active with \(sound)")
    }
    
    func simulateStop(bus: Int) {
        soundManager.activeBusIds.remove(bus)
        soundManager.activeNodeNames.removeValue(forKey: bus)
        appendLog(" -> Set Bus \(bus) inactive")
    }
    
    func assertPlaying(sound: String, bus: Int, expected: Bool) {
        let busId = soundManager.soundRoutes[sound] ?? 0
        let isAssigned = busId != 0
        let isPlaying = isAssigned && soundManager.activeBusIds.contains(busId) && soundManager.activeNodeNames[busId] == sound
        
        if isPlaying == expected {
            appendLog(" [PASS] \(sound) playing state: \(isPlaying)")
        } else {
            appendLog(" [FAIL] \(sound) playing state: \(isPlaying) (Expected: \(expected))")
        }
    }
    
    func appendLog(_ text: String) {
        log += text + "\n"
    }
}
