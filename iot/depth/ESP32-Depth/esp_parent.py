import uwebsockets.client
import ujson
import time
from machine import Pin
import neopixel

# ============================================================
# CONFIGURATION
# ============================================================

SERVER_URL = "ws://192.168.1.133:8080"

# Boutons (GPIO -> bouton -> GND)
BUTTON_PINS = {
    1: 14,
    2: 19,
    3: 23,
}
buttons = {n: Pin(p, Pin.IN, Pin.PULL_UP) for n, p in BUTTON_PINS.items()}

# WS2812
LED_PIN = 27

# Zones LED (VARIABLES — À AJUSTER PLUS TARD)
ZONE_LEDS = {
    1: (0, 4),
    2: (5, 9),
    3: (10, 14),
}

NUM_LEDS = max(end for (_, end) in ZONE_LEDS.values()) + 1
np = neopixel.NeoPixel(Pin(LED_PIN), NUM_LEDS)

# Timing
SEQUENCE_ON = 0.5
SEQUENCE_OFF = 0.2
INACTIVITY_TIMEOUT = 20
DEBOUNCE = 0.2

# ============================================================
# JSON STATE MANAGEMENT
# ============================================================

state = {}

def empty_state():
    return {
        # Rift table
        "children_rift_part_count": None,
        "parent_rift_part_count": None,

        # Step 1 - Stranger
        "start_system": None,
        "recognized_stranger_name": None,
        "pinguin_micro": None,
        "pinguin_audio": None,

        # Step 2 - Depth
        "step_1_parent_sucess": None,
        "step_2_parent_sucess": None,
        "step_3_parent_sucess": None,
        "step_1_enfant_sucess": None,
        "step_2_enfant_sucess": None,
        "step_3_enfant_sucess": None,

        # Step 3 - Imagination
        "torch_scanned": None,
        "cage_is_on_monster": None,

        # Scenographie
        "preset_stranger": None,
        "preset_depth": None,
        "preset_imagination": None,
        "preset_ending": None,
    }

def merge_state(incoming):
    for k, v in incoming.items():
        if v is not None:
            state[k] = v

def send_state(ws, key, value):
    payload = empty_state()
    payload[key] = value
    ws.send(ujson.dumps(payload))
    print(">", payload)

# ============================================================
# LED HELPERS
# ============================================================

def clear_leds():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

def light_zone(zone, color=(80, 80, 80)):
    start, end = ZONE_LEDS[zone]
    for i in range(start, end + 1):
        np[i] = color
    np.write()

def flash_zone(zone):
    light_zone(zone, (150, 150, 150))
    time.sleep(0.1)
    clear_leds()

# ============================================================
# INPUT HANDLING
# ============================================================

input_locked = False

def read_button():
    global input_locked
    if input_locked:
        return None

    for n, b in buttons.items():
        if b.value() == 0:
            print("[BTN]", n)
            flash_zone(n)
            time.sleep(DEBOUNCE)
            return n
    return None

# ============================================================
# GAME LOGIC (DEPTH)
# ============================================================

PARTITIONS = {
    1: [1, 2, 1, 3],
    2: [3, 3, 1],
    3: [2, 1, 2, 3],
}

def depth_active():
    return (
        state.get("preset_depth") is True and
        (state.get("children_rift_part_count", 0) +
         state.get("parent_rift_part_count", 0)) == 2
    )

def determine_step():
    for i in (1, 2, 3):
        if state.get(f"step_{i}_parent_sucess") is None:
            return i
    return None

def show_sequence(part):
    global input_locked
    input_locked = True

    print("[LED] Show sequence:", part)
    clear_leds()

    for step in part:
        light_zone(step)
        time.sleep(SEQUENCE_ON)
        clear_leds()
        time.sleep(SEQUENCE_OFF)

    input_locked = False
    print("[LED] Sequence end")

def play_parent(part):
    show_sequence(part)

    idx = 0
    last_input = time.time()

    while idx < len(part):
        now = time.time()

        # Inactivity → replay
        if now - last_input > INACTIVITY_TIMEOUT:
            print("[TIMEOUT] Replay sequence")
            idx = 0
            show_sequence(part)
            last_input = time.time()
            continue

        btn = read_button()
        if btn:
            last_input = now

            if btn == part[idx]:
                print("[OK]", btn)
                idx += 1
            else:
                print("[ERR] Got", btn, "expected", part[idx])
                idx = 0
                show_sequence(part)

        time.sleep(0.01)

    return True

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    print("ESP PARENT → Connecting WS...")
    ws = uwebsockets.client.connect(SERVER_URL)

    while True:
        # Receive JSON global
        try:
            raw = ws.recv()
            merge_state(ujson.loads(raw))
        except:
            pass

        if not depth_active():
            time.sleep(0.05)
            continue

        step = determine_step()
        if step is None:
            time.sleep(0.05)
            continue

        child_key = f"step_{step}_enfant_sucess"
        parent_key = f"step_{step}_parent_sucess"

        # Parent plays only after child success
        if state.get(child_key) is True and state.get(parent_key) is None:
            print("[DEPTH] Parent playing step", step)
            if play_parent(PARTITIONS[step]):
                send_state(ws, parent_key, True)
                state[parent_key] = True

        time.sleep(0.01)

main()