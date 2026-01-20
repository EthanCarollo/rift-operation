"""
Operator Hardware Test Script
Tests all components individually:
- Button
- LED Prompt (blink)
- LED Step 1/2/3
"""

from machine import Pin
import uasyncio as asyncio
import time

print("=" * 50)
print("OPERATOR HARDWARE TEST")
print("=" * 50)

# Initialize components
print("\n[1/5] Initializing Button (GPIO 32)...")
button = Pin(32, Pin.IN, Pin.PULL_UP)
print("✓ Button ready")

print("\n[2/5] Initializing LED Prompt (GPIO 33)...")
led_prompt = Pin(33, Pin.OUT)
led_prompt.off()
print("✓ LED Prompt ready")

print("\n[3/5] Initializing LED Step 1 (GPIO 25)...")
led_step_1 = Pin(25, Pin.OUT)
led_step_1.off()
print("✓ LED Step 1 ready")

print("\n[4/5] Initializing LED Step 2 (GPIO 26)...")
led_step_2 = Pin(26, Pin.OUT)
led_step_2.off()
print("✓ LED Step 2 ready")

print("\n[5/5] Initializing LED Step 3 (GPIO 14)...")
led_step_3 = Pin(14, Pin.OUT)
led_step_3.off()
print("✓ LED Step 3 ready")

print("\n" + "=" * 50)
print("RUNNING TESTS")
print("=" * 50)

async def test_sequence():
    # Test 1: LED Prompt Blink
    print("\n[TEST 1] LED Prompt - Blink 5 times...")
    for i in range(5):
        led_prompt.on()
        await asyncio.sleep_ms(300)
        led_prompt.off()
        await asyncio.sleep_ms(300)
    print("✓ LED Prompt test complete")
    
    # Test 2: Step LEDs Sequential
    print("\n[TEST 2] Step LEDs - Sequential light up...")
    print("  → Step 1 ON")
    led_step_1.on()
    await asyncio.sleep(1)
    
    print("  → Step 2 ON")
    led_step_2.on()
    await asyncio.sleep(1)
    
    print("  → Step 3 ON")
    led_step_3.on()
    await asyncio.sleep(1)
    
    print("  → All OFF")
    led_step_1.off()
    led_step_2.off()
    led_step_3.off()
    await asyncio.sleep(1)
    print("✓ Step LEDs test complete")
    
    # Test 3: Button
    print("\n[TEST 3] Button - Press button within 5 seconds...")
    start_time = time.time()
    button_pressed = False
    
    while time.time() - start_time < 5:
        if button.value() == 0:  # Active low
            if not button_pressed:
                print("✓ Button press detected!")
                led_prompt.on()
                await asyncio.sleep_ms(100)
                led_prompt.off()
                button_pressed = True
        await asyncio.sleep_ms(50)
    
    if not button_pressed:
        print("✗ No button press detected")
    
    # Test 4: All LEDs ON
    print("\n[TEST 4] All LEDs ON for 2 seconds...")
    led_prompt.on()
    led_step_1.on()
    led_step_2.on()
    led_step_3.on()
    await asyncio.sleep(2)
    
    # All OFF
    led_prompt.off()
    led_step_1.off()
    led_step_2.off()
    led_step_3.off()
    print("✓ All LEDs test complete")
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETE!")
    print("=" * 50)

# Run tests
asyncio.run(test_sequence())
