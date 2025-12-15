import time
import ujson as json
from machine import Pin
from src.Framework.EspController import EspController


class DepthController(EspController):

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "DepthController"

        self.role = config.depth.role
        self.partitions = config.depth.partitions
        self.current_partition = None

        # Boutons
        self.buttons = {
            name: Pin(pin, Pin.IN, Pin.PULL_UP)
            for name, pin in config.depth.button_pins.items()
        }

        # LEDs uniquement pour le parent
        self.leds = None
        if self.role == "parent":
            self.leds = {
                name: Pin(pin, Pin.OUT)
                for name, pin in config.depth.led_pins.items()
            }

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------

    def depth_is_active(self):
        state = self.websocket_client.state
        return (
            state.get("preset_depth") is True
            and state.get("children_rift_part_count", 0)
            + state.get("parent_rift_part_count", 0) == 2
        )

    def get_current_step(self):
        for step in (1, 2, 3):
            key = f"step_{step}_{self.role}_sucess"
            if self.websocket_client.state.get(key) is None:
                return step
        return None

    def read_button(self):
        for name, button in self.buttons.items():
            if button.value() == 0:
                time.sleep(0.2)  # debounce
                return name
        return None

    # ------------------------------------------------------------------
    # LEDs (parent only)
    # ------------------------------------------------------------------

    def play_led_sequence(self, sequence):
        if not self.leds:
            return

        for led in sequence:
            self.leds[led].value(1)
            time.sleep(0.4)
            self.leds[led].value(0)
            time.sleep(0.2)

    # ------------------------------------------------------------------
    # Gameplay
    # ------------------------------------------------------------------

    def play_partition(self, sequence):
        """
        Logique de jeu commune parent / enfant
        """
        if self.role == "parent":
            self.play_led_sequence(sequence)

        index = 0

        while index < len(sequence):
            btn = self.read_button()
            if not btn:
                time.sleep(0.01)
                continue

            if btn == sequence[index]:
                index += 1
            else:
                index = 0

        return True

    # ------------------------------------------------------------------
    # WebSocket
    # ------------------------------------------------------------------

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.websocket_client.merge_state(data)

            if data.get("type") == "partition":
                self.current_partition = list(
                    map(int, data["value"].split(","))
                )
                self.logger.info(f"Partition reçue : {self.current_partition}")

            elif data.get("type") == "unlock":
                self.logger.info("Action finale déclenchée")

        except Exception as e:
            self.logger.error(f"Message invalide : {e}")

    # ------------------------------------------------------------------
    # Game loop (appelé par EspController)
    # ------------------------------------------------------------------

    async def update(self):

        if not self.depth_is_active():
            return

        # 1. Partition envoyée dynamiquement
        if self.current_partition:
            if self.play_partition(self.current_partition):
                await self.websocket_client.send(
                    json.dumps({"type": "message", "value": "success"})
                )
                self.current_partition = None
            return

        # 2. Mode steps classiques
        step = self.get_current_step()
        if step is None:
            return

        # Parent attend la réussite de l’enfant
        if self.role == "parent":
            child_key = f"step_{step}_child_sucess"
            if self.websocket_client.state.get(child_key) is not True:
                return

        partition = self.partitions.get(step, [])
        if not partition:
            return

        self.logger.info(f"{self.role} joue l'étape {step}")

        if self.play_partition(partition):
            key = f"step_{step}_{self.role}_sucess"
            self.websocket_client.send_state(key, True)
            self.websocket_client.state[key] = True