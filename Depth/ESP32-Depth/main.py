import uwebsockets.client
import ujson
import os
from machine import Pin
import time
import select

ROLE = "child"
SERVER_URL = "ws://192.168.1.133:8080"

BUTTON_PINS = {1: 14, 2: 19, 3: 23}
buttons = {n: Pin(p, Pin.IN, Pin.PULL_UP) for n, p in BUTTON_PINS.items()}

if ROLE == "parent":
    LED_PINS = {1: 25, 2: 32, 3: 33}
    leds = {n: Pin(p, Pin.OUT) for n, p in LED_PINS.items()}


def send(ws, t, v):
    msg = ujson.dumps({"type": t, "value": v})
    ws.send(msg)
    print(">", msg)

# --- NEW: NON BLOQUING BUTTON DETECTION ---
def read_button():
    for n, b in buttons.items():
        if b.value() == 0:
            print("[LOG] Bouton", n, "pressé")
            time.sleep(0.2)  # anti-rebond
            return n
    return None

def show_leds(part):
    if ROLE != "parent":
        return

    print("[LOG] Séquence LEDs:", part)
    for n in part:
        print(f"[LOG] LED {n} ON")
        leds[n].value(1)
        time.sleep(0.4)
        print(f"[LOG] LED {n} OFF")
        leds[n].value(0)
        time.sleep(0.2)


def play_child(part):
    idx = 0
    print("[LOG] Enfant doit jouer:", part)
    while idx < len(part):
        btn = read_button()
        if btn:
            if btn == part[idx]:
                print("[LOG] OK - bouton correct")
                idx += 1
            else:
                print("[LOG] Mauvais bouton -> reset")
                idx = 0
        time.sleep(0.01)
    return True


def play_parent(part):
    show_leds(part)
    idx = 0
    print("[LOG] Parent doit jouer:", part)
    while idx < len(part):
        btn = read_button()
        if btn:
            if btn == part[idx]:
                print("[LOG] OK - bouton correct")
                idx += 1
            else:
                print("[LOG] Mauvais bouton -> reset")
                idx = 0
        time.sleep(0.01)
    return True


def main():
    print("Connecting WS...")
    ws = uwebsockets.client.connect(SERVER_URL)
    send(ws, "register", ROLE)

    current_partition = None

    while True:
        # --- CHECK INCOMING WS WITHOUT BLOCKING ---
        try:
            raw = ws.recv()  # If no data, will throw
            msg = ujson.loads(raw)
            print("<", msg)

            if msg["type"] == "partition":
                current_partition = list(map(int, msg["value"].split(",")))

            elif msg["type"] == "unlock":
                print("⚡ ACTION FINALE ⚡")

        except:
            pass  # No message → continue running

        # --- EXECUTE PARTITION IF AVAILABLE ---
        if current_partition:
            ok = play_child(current_partition) if ROLE == "child" else play_parent(current_partition)
            if ok:
                print("[LOG] Partition réussie → envoi success")
                send(ws, "message", "success")
                current_partition = None

        time.sleep(0.01)  # CPU friendly


main()