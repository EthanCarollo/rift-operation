import time
import ujson as json
from machine import Pin
from src.Framework.EspController import EspController
from src.Core.Depth.DepthConfig import DepthConfigFactory


class DepthController(EspController):

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "DepthController"
        self.depthConfig = DepthConfigFactory.create_default_child()

        self.role = self.depthConfig.depth.role  # "parent" ou "enfant"
        self.partitions = self.depthConfig.depth.partitions

        self.state = {}               # état global reçu du serveur
        self.is_playing = False
        self.device_id = config.device_id

        # Boutons
        self.buttons = {
            name: Pin(pin, Pin.IN, Pin.PULL_UP)
            for name, pin in self.depthConfig.depth.button_pins.items()
        }

        # LEDs uniquement pour le parent
        self.leds = None
        if self.role == "parent":
            self.leds = {
                name: Pin(pin, Pin.OUT)
                for name, pin in self.depthConfig.depth.led_pins.items()
            }

    # --------------------------------------------------
    # Conditions métier
    # --------------------------------------------------

    def depth_started(self):
        return (
            self.state.get("dream_rift_part_count") == 1
            and self.state.get("nightmare_rift_part_count") == 1
        )

    def depth_finished(self):
        return (
            self.state.get("depth_step_3_parent_sucess") == True
            and self.state.get("depth_step_3_enfant_sucess") == True
        )

    def current_step(self):
        for step in (1, 2, 3):
            key = f"depth_step_{step}_{self.role}_sucess"
            if self.state.get(key) is not True:
                return step
        return None

    # --------------------------------------------------
    # Inputs
    # --------------------------------------------------

    def read_button(self):
        for name, button in self.buttons.items():
            if button.value() == 0:
                self.logger.info(f"🔘 Bouton détecté : {name}")
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
        self.logger.info(f"🎮 Démarrage partition : {sequence}")

        while index < len(sequence):
            btn = self.read_button()
            if not btn:
                time.sleep(0.01)
                continue

            attendu = sequence[index]

            if btn == attendu:
                self.logger.info(
                    f"✅ Bon bouton : {btn} ({index + 1}/{len(sequence)})"
                )
                index += 1
            else:
                self.logger.info(
                    f"❌ Mauvais bouton : {btn} (attendu {attendu}) → reset"
                )
                index = 0

        self.logger.info("🎉 Partition réussie !")
        return True

    # --------------------------------------------------
    # WebSocket
    # --------------------------------------------------

    async def process_message(self, message):
        try:
            data = json.loads(message)
            self.state = data
            self.logger.info("📡 État global reçu")
        except Exception as e:
            self.logger.error(f"JSON invalide : {e}")

    # --------------------------------------------------
    # Loop principale
    # --------------------------------------------------

    async def update(self):

        if not self.depth_started():
            self.is_playing = False
            return

        if self.is_playing:
            return

        step = self.current_step()
        if step is None:
            return

        # 🔒 Parent attend l’enfant (step en cours)
        if self.role == "parent":
            child_key = f"depth_step_{step}_enfant_sucess"
            if self.state.get(child_key) is not True:
                self.logger.info(
                    f"⏳ Parent attend enfant (step {step})"
                )
                return

        # 🔒 Enfant attend le parent (step précédent)
        if self.role == "enfant" and step > 1:
            parent_prev_key = f"depth_step_{step - 1}_parent_sucess"
            if self.state.get(parent_prev_key) is not True:
                self.logger.info(
                    f"⏳ Enfant attend parent (step {step - 1})"
                )
                return

        partition = self.partitions.get(step)
        if not partition:
            return

        self.is_playing = True
        self.logger.info(f"🚀 {self.role.upper()} joue step {step}")

        if self.play_partition(partition):

            key = f"depth_step_{step}_{self.role}_sucess"
            self.state[key] = True

            self.logger.info(
                f"📤 Envoi JSON global mis à jour ({key}=true)"
            )

            await self.websocket_client.send(
                json.dumps(self.state)
            )

            if self.depth_finished():
                self.logger.info("🏁 Depth terminée")
                await self.websocket_client.send(
                    json.dumps(self.state)
                )

        self.is_playing = False


