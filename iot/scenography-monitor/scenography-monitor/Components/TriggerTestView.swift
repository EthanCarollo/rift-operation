import SwiftUI
import Combine

struct TriggerTestView: View {
    @State private var logs: [String] = []
    
    var body: some View {
        VStack {
            Text("Trigger Replay Test")
                .font(.headline)
            
            ScrollView {
                VStack(alignment: .leading) {
                    ForEach(logs, id: \.self) { log in
                        Text(log)
                            .font(.system(.body, design: .monospaced))
                            .foregroundColor(log.contains("FAIL") ? .red : .green)
                    }
                }
                .padding()
            }
            .frame(height: 300)
            .border(Color.gray)
            
            Button("Run Test") {
                runTest()
            }
            .padding()
        }
    }
    
    func runTest() {
        logs = []
        log("Starting Test...")
        
        let trigger = SoundTrigger.shared
        let testKey = "test_event"
        let testSound = "test_sound"
        
        // 1. Setup Binding
        // 1. Setup Binding
        trigger.addBinding(key: testKey, sound: testSound, instanceId: UUID(), value: "true")
        log("Binding added: \(testKey) -> \(testSound) (Target: true)")
        
        // 2. Simulate First Event
        log("Sending Event 1: { \(testKey): true }")
        
        // We need to simulate WebSocketManager update. 
        // Since we can't easily write to WebSocketManager's stream directly from here without access, 
        // we will use a workaround or manual injection if SoundTrigger allowed it.
        // Actually, SoundTrigger listens to WebSocketManager.shared.$latestData.
        // We can simulate an update by setting WebSocketManager.shared.latestData if it's accessible.
        // Checking WebSocketManager... it is a singleton with @Published. We can assign to it!
        
        // Mocking the trigger action by observing the impact?
        // SoundTrigger calls SoundManager.playSound.
        // We can't easily mock SoundManager, but we can check if SoundManager received a call? 
        // No, SoundManager is a singleton.
        // Workaround: We will rely on SoundTrigger logging or internal state if possible.
        // Or, we assume if we send the event, SoundTrigger logic *should* print.
        // BETTER: let's modify SoundTrigger to have a callback for testing? 
        // Or just observe console logs? The user won't see console logs in the UI easily.
        
        // Let's TRY to rely on SoundManager's activeBusIds or last played?
        // SoundManager doesn't expose "last played sound".
        
        // For this test to be robust, I will first modify SoundTrigger to expose a `onTrigger` callback.
        
        WebSocketManager.shared.handleMessage("{\"\(testKey)\": true}")
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            log("Wait 0.5s...")
            
            // 3. Simulate Second Event (Replay)
            log("Sending Event 2: { \(testKey): true }")
            WebSocketManager.shared.handleMessage("{\"\(testKey)\": true}")
            
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                log("Test Finished. Check console for 'Triggering Sound' messages.")
                log("Expected: 2 Triggers.")
                log("Current Behavior: Likely 1 Trigger.")
            }
        }
    }
    
    func log(_ msg: String) {
        logs.append(msg)
        print("[TEST] \(msg)")
    }
}
