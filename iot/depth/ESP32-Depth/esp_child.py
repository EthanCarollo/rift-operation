import uwebsockets.client
import ujson
import time
from machine import Pin

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
# INPUT HANDLING
# ============================================================

def read_button():
    for n, b in buttons.items():
        if b.value() == 0:
            print("[BTN]", n)
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
        if state.get(f"step_{i}_enfant_sucess") is None:
            return i
    return None

def play_child(part):
    print("[CHILD] Play:", part)
    idx = 0

    while idx < len(part):
        btn = read_button()
        if btn:
            if btn == part[idx]:
                print("[OK]", btn)
                idx += 1
            else:
                print("[ERR] Got", btn, "expected", part[idx])
                idx = 0
        time.sleep(0.01)

    return True

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    print("ESP CHILD → Connecting WS...")
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

        key = f"step_{step}_enfant_sucess"

        if state.get(key) is None:
            print("[DEPTH] Child playing step", step)
            if play_child(PARTITIONS[step]):
                send_state(ws, key, True)
                state[key] = True

        time.sleep(0.01)

main()