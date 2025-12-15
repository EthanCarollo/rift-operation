import time
import ujson as json
from machine import Pin
from src.Framework.EspController import EspController


class DepthController(EspController):

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "DepthController"

        self.role = config.depth.role  # "parent" ou "enfant"
        self.partitions = config.depth.partitions

        self.state = {}               # état global reçu du serveur
        self.is_playing = False       # évite de rejouer en boucle

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

    # --------------------------------------------------
    # Conditions métier
    # --------------------------------------------------

    def depth_started(self):
        return (
            self.state.get("preset_depth") is True
            and self.state.get("children_rift_part_count") == 1
            and self.state.get("parent_rift_part_count") == 1
        )

    def depth_finished(self):
        return (
            self.state.get("children_rift_part_count") == 2
            and self.state.get("parent_rift_part_count") == 2
        )

    def current_step(self):
        for step in (1, 2, 3):
            key = f"step_{step}_{self.role}_sucess"
            if self.state.get(key) is not True:
                return step
        return None

    # --------------------------------------------------
    # Inputs / Outputs
    # --------------------------------------------------

    def read_button(self):
        for name, button in self.buttons.items():
            if button.value() == 0:
                self.logger.info(f"BOUTON DÉTECTÉ : {name}")
                time.sleep(0.2)
                return name
        return None

    def play_leds(self, sequence):
        if not self.leds:
            return
        for led in sequence:
            self.leds[led].value(1)
            time.sleep(0.4)
            self.leds[led].value(0)
            time.sleep(0.2)

    # --------------------------------------------------
    # Gameplay
    # --------------------------------------------------

    def play_partition(self, sequence):
        if self.role == "parent":
            self.play_leds(sequence)

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

    # --------------------------------------------------
    # WebSocket
    # --------------------------------------------------

    async def process_message(self, message):
        try:
            self.logger.info("recus message")
            data = json.loads(message)
            self.state = data  # snapshot complet de l'état serveur
        except Exception as e:
            self.logger.error(f"JSON invalide : {e}")

    # --------------------------------------------------
    # Loop principale (appelée par EspController)
    # --------------------------------------------------

    async def update(self):

        # Expérience pas encore lancée
        if not self.depth_started():
            self.is_playing = False
            return

        # Expérience déjà terminée
        if self.depth_finished():
            self.logger.info("Depth terminée")
            return

        # Empêche de relancer pendant qu'on joue
        if self.is_playing:
            return

        step = self.current_step()
        if step is None:
            return

        # Le parent attend que l'enfant ait réussi l'étape
        if self.role == "parent":
            child_key = f"step_{step}_enfant_sucess"
            if self.state.get(child_key) is not True:
                return

        partition = self.partitions.get(step)
        if not partition:
            return

        self.is_playing = True
        self.logger.info(f"{self.role} joue l'étape {step}")

        if self.play_partition(partition):
            key = f"step_{step}_{self.role}_sucess"
            await self.websocket_client.send(
                json.dumps({key: True})
            )

        self.is_playing = False

