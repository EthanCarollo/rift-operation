"""
Tests for LedStrip and LedController modules.
Run on MicroPython ESP32 with: exec(open('test/test_led.py').read())
"""

import sys
sys.path.insert(0, '/') # Ensure root is in path for imports

# ============================================
# CONFIGURATION - Edit these values as needed
# ============================================

# Hardware config
TEST_PIN = 5
TEST_NUM_PIXELS = 10

# Test animation with alpha
TEST_ANIMATION_ALPHA = {
    "name": "Test Animation Alpha",
    "frames": [
        {
            "time": 100,
            "colors": [
                {"color": "255,0,0,0.5", "position": 0},
                {"color": "0,0,255,0.5", "position": 100}
            ]
        }
    ]
}

# Solid color animation for alpha testing
TEST_ANIMATION_SOLID = {
    "frames": [
        {
            "time": 100,
            "colors": [
                {"color": "100,200,255,0.25", "position": 0},
                {"color": "100,200,255,0.25", "position": 100}
            ]
        }
    ]
}

# Gradient animation for interpolation testing
TEST_ANIMATION_GRADIENT = {
    "frames": [
        {
            "time": 100,
            "colors": [
                {"color": "255,0,0,1.0", "position": 0},
                {"color": "0,0,255,1.0", "position": 100}
            ]
        }
    ]
}

# ============================================


# --- TEST UTILITIES ---
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def ok(self, name):
        self.passed += 1
        print(f"  [OK] {name}")
    
    def fail(self, name, msg=""):
        self.failed += 1
        self.errors.append((name, msg))
        print(f"  [FAIL] {name}: {msg}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*40}")
        print(f"Results: {self.passed}/{total} passed")
        if self.errors:
            print("Failures:")
            for name, msg in self.errors:
                print(f"  - {name}: {msg}")
        print('='*40)
        return self.failed == 0


def assert_eq(actual, expected, name, result):
    if actual == expected:
        result.ok(name)
    else:
        result.fail(name, f"expected {expected}, got {actual}")


def assert_close(actual, expected, tolerance, name, result):
    if abs(actual - expected) <= tolerance:
        result.ok(name)
    else:
        result.fail(name, f"expected ~{expected}, got {actual}")


# --- LED STRIP TESTS ---
def test_led_strip(result):
    print("\n--- LedStrip Tests ---")
    
    from src.Framework.Led.LedStrip import LedStrip
    
    strip = LedStrip(pin_id=TEST_PIN, num_pixels=TEST_NUM_PIXELS)
    
    # Test: initialization
    assert_eq(strip.num_pixels, TEST_NUM_PIXELS, "num_pixels init", result)
    
    # Test: set_pixel RGB
    strip.set_pixel(0, (255, 128, 64))
    assert_eq(strip.np[0], (255, 128, 64), "set_pixel RGB", result)
    
    # Test: set_pixel RGBA with alpha=1.0
    strip.set_pixel(1, (100, 100, 100, 1.0))
    assert_eq(strip.np[1], (100, 100, 100), "set_pixel RGBA alpha=1.0", result)
    
    # Test: set_pixel RGBA with alpha=0.5 -> colors halved
    strip.set_pixel(2, (200, 100, 50, 0.5))
    r, g, b = strip.np[2]
    assert_eq(r, 100, "set_pixel alpha=0.5 R", result)
    assert_eq(g, 50, "set_pixel alpha=0.5 G", result)
    assert_eq(b, 25, "set_pixel alpha=0.5 B", result)
    
    # Test: set_pixel RGBA with alpha=0.2
    strip.set_pixel(3, (255, 255, 255, 0.2))
    r, g, b = strip.np[3]
    assert_eq(r, 51, "set_pixel alpha=0.2 R", result)
    assert_eq(g, 51, "set_pixel alpha=0.2 G", result)
    assert_eq(b, 51, "set_pixel alpha=0.2 B", result)
    
    # Test: set_pixel RGBA with alpha=0 -> black
    strip.set_pixel(4, (255, 0, 0, 0.0))
    assert_eq(strip.np[4], (0, 0, 0), "set_pixel alpha=0", result)
    
    # Test: clear
    strip.clear()
    assert_eq(strip.np[0], (0, 0, 0), "clear", result)


# --- LED CONTROLLER TESTS ---
def test_led_controller(result):
    print("\n--- LedController Tests ---")
    
    from src.Framework.Led.LedStrip import LedStrip
    from src.Framework.Led.LedController import LedController
    
    strip = LedStrip(pin_id=TEST_PIN, num_pixels=TEST_NUM_PIXELS)
    controller = LedController(strip)
    
    # Test: initial state
    assert_eq(controller.is_playing, False, "initial is_playing", result)
    assert_eq(controller.brightness, 1.0, "initial brightness", result)
    
    # Test: set_brightness
    controller.set_brightness(0.5)
    assert_eq(controller.brightness, 0.5, "set_brightness", result)
    
    controller.set_brightness(1.5)  # Clamp to 1.0
    assert_eq(controller.brightness, 1.0, "set_brightness clamp max", result)
    
    controller.set_brightness(-0.5)  # Clamp to 0.0
    assert_eq(controller.brightness, 0.0, "set_brightness clamp min", result)
    
    controller.set_brightness(1.0)  # Reset
    
    controller.play(TEST_ANIMATION_ALPHA, loop=False)
    assert_eq(controller.is_playing, True, "play starts animation", result)
    assert_eq(controller.num_frames, 1, "correct frame count", result)
    
    # Test: rendered frame has correct alpha
    frame_pixels = controller.rendered_frames[0]
    
    # First pixel should be red with alpha 0.5
    r, g, b, a = frame_pixels[0]
    assert_eq(r, 255, "first pixel R", result)
    assert_eq(g, 0, "first pixel G", result)
    assert_eq(b, 0, "first pixel B", result)
    assert_close(a, 0.5, 0.01, "first pixel alpha", result)
    
    # Last pixel should be blue with alpha 0.5
    r, g, b, a = frame_pixels[-1]
    assert_eq(r, 0, "last pixel R", result)
    assert_eq(g, 0, "last pixel G", result)
    assert_eq(b, 255, "last pixel B", result)
    assert_close(a, 0.5, 0.01, "last pixel alpha", result)
    
    # Test: stop
    controller.stop()
    assert_eq(controller.is_playing, False, "stop animation", result)


def test_alpha_application(result):
    """Test that alpha is correctly applied when rendering to strip."""
    print("\n--- Alpha Application Tests ---")
    
    from src.Framework.Led.LedStrip import LedStrip
    from src.Framework.Led.LedController import LedController
    
    strip = LedStrip(pin_id=TEST_PIN, num_pixels=5)
    controller = LedController(strip)
    
    controller.play(TEST_ANIMATION_SOLID, loop=False)
    
    # Check rendered frame alpha
    r, g, b, a = controller.rendered_frames[0][0]
    assert_eq(r, 100, "solid color R", result)
    assert_eq(g, 200, "solid color G", result)
    assert_eq(b, 255, "solid color B", result)
    assert_close(a, 0.25, 0.01, "solid color alpha", result)
    
    # Manually render and check strip
    controller._render_pixels(controller.rendered_frames[0])
    
    # Strip should have RGB values multiplied by alpha (0.25)
    pr, pg, pb = strip.np[0]
    assert_eq(pr, 25, "strip pixel R (100 * 0.25)", result)
    assert_eq(pg, 50, "strip pixel G (200 * 0.25)", result)
    assert_eq(pb, 63, "strip pixel B (255 * 0.25)", result)


def test_gradient_interpolation(result):
    """Test gradient color interpolation."""
    print("\n--- Gradient Interpolation Tests ---")
    
    from src.Framework.Led.LedStrip import LedStrip
    from src.Framework.Led.LedController import LedController
    
    strip = LedStrip(pin_id=TEST_PIN, num_pixels=5)
    controller = LedController(strip)
    
    controller.play(TEST_ANIMATION_GRADIENT, loop=False)
    pixels = controller.rendered_frames[0]
    
    # First pixel = pure red
    assert_eq(pixels[0][0], 255, "gradient start R", result)
    assert_eq(pixels[0][2], 0, "gradient start B", result)
    
    # Last pixel = pure blue
    assert_eq(pixels[-1][0], 0, "gradient end R", result)
    assert_eq(pixels[-1][2], 255, "gradient end B", result)
    
    # Middle pixel should be ~50% blend (127 or 128)
    mid = len(pixels) // 2
    mid_r = pixels[mid][0]
    mid_b = pixels[mid][2]
    
    if 100 <= mid_r <= 155 and 100 <= mid_b <= 155:
        result.ok("gradient middle blend")
    else:
        result.fail("gradient middle blend", f"R={mid_r}, B={mid_b}")


# --- RUN ALL TESTS ---
def run_all():
    print("="*40)
    print("LED Module Test Suite")
    print("="*40)
    
    result = TestResult()
    
    try:
        test_led_strip(result)
    except Exception as e:
        result.fail("test_led_strip", str(e))
    
    try:
        test_led_controller(result)
    except Exception as e:
        result.fail("test_led_controller", str(e))
    
    try:
        test_alpha_application(result)
    except Exception as e:
        result.fail("test_alpha_application", str(e))
    
    try:
        test_gradient_interpolation(result)
    except Exception as e:
        result.fail("test_gradient_interpolation", str(e))
    
    return result.summary()


if __name__ == "__main__":
    run_all()
