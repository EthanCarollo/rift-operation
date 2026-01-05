import uasyncio as asyncio
import ujson as json
from machine import Pin
from src.Framework.EspController import EspController
from src.Framework.Led.LedStrip import LedStrip
from src.Framework.Led.LedController import LedController as FrameworkLedController
from src.Core.Depth.DepthConfig import DepthConfigFactory


class DepthController(EspController):

    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "DepthController"
        self.depthConfig = DepthConfigFactory.create_default_child()

        self.role = self.depthConfig.depth.role  # "nightmare" ou "dream"
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
        if self.role == "nightmare":
            self.leds = {
                name: Pin(pin, Pin.OUT)
                for name, pin in self.depthConfig.depth.led_pins.items()
            }

        # LED strip (animations JSON) uniquement pour nightmare
        self.led_strip = None
        self.led_controller = None
        self.led_anim_mapping = {
            1: "data/depth/nightmare/step1_show.json",
            2: "data/depth/nightmare/step2_show.json",
            3: "data/depth/nightmare/step3_show.json",
        }

        if self.role == "nightmare":
            try:
                strip_pin = getattr(self.depthConfig.depth, "led_strip_pin", 4)
                strip_count = getattr(self.depthConfig.depth, "led_strip_count", 20)
                self.led_strip = LedStrip(strip_pin, strip_count)
                self.led_strip.clear()

                self.led_controller = FrameworkLedController(self.led_strip)
                self.led_controller.start_thread()
                self.logger.info(
                    f"💡 LED strip initialisée (pin={strip_pin}, count={strip_count})"
                )
            except Exception as e:
                self.logger.warning(f"⚠️ LED strip non initialisée : {e}")

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
            self.state.get("depth_step_3_nightmare_sucess") == True
            and self.state.get("depth_step_3_dream_sucess") == True
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

    async def read_button(self):
        for name, button in self.buttons.items():
            if button.value() == 0:
                self.logger.info(f"🔘 Bouton détecté : {name}")
                await asyncio.sleep(0.2)
                return name
        return None

    async def play_leds(self, sequence):
        if not self.leds:
            return
        for led in sequence:
            # Check reset during LED sequence
            if self.state.get("reset_system"):
                return
            
            self.leds[led].value(1)
            await asyncio.sleep(0.4)
            self.leds[led].value(0)
            await asyncio.sleep(0.2)

    async def play_led_intro(self, step, sequence):
        """Joue l'animation LED du step (strip JSON si dispo, sinon fallback GPIO)."""
        if self.state.get("reset_system"):
            return False

        # Strip animations (JSON)
        if self.led_controller:
            anim_file = self.led_anim_mapping.get(step)
            if anim_file:
                self.logger.info(f"💡 LEDs step {step} : {anim_file}")
                self.led_controller.play_from_json(anim_file, loop=False)

                while self.led_controller.is_playing:
                    if self.state.get("reset_system"):
                        self.led_controller.stop()
                        return False
                    await asyncio.sleep(0.05)
            return True

        # Fallback: LEDs GPIO en séquence
        await self.play_leds(sequence)
        return not self.state.get("reset_system")

    # --------------------------------------------------
    # Gameplay
    # --------------------------------------------------

    async def play_partition(self, step, sequence):
        if self.role == "nightmare":
            leds_ok = await self.play_led_intro(step, sequence)
            if not leds_ok:
                self.logger.info("🔄 Reset demandé pendant l'animation LEDs")
                return False

        index = 0
        self.logger.info(f"🎮 Démarrage partition : {sequence}")

        while index < len(sequence):
            
            # 🛑 Check Reset
            if self.state.get("reset_system"):
                self.logger.info("🔄 Reset demandé - Arrêt partition")
                return False

            btn = await self.read_button()
            
            if not btn:
                await asyncio.sleep(0.05)
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
        
        # 0. Check Reset System
        if self.state.get("reset_system") is True:
            # On ne fait rien, on attend que le reset passe à False
            # (Le serveur devrait le repasser à null/false après avoir reset ?)
            # Ou alors on réinitialise l'état local si besoin
            if self.is_playing:
                self.is_playing = False
                self.logger.info("🔄 Reset actif - Système en pause")
            
            await asyncio.sleep(1)
            return

        if not self.depth_started():
            self.is_playing = False
            return

        if self.is_playing:
            return

        step = self.current_step()
        if step is None:
            return

        # 🔒 Nightmare attend le dream (step en cours)
        if self.role == "nightmare":
            child_key = f"depth_step_{step}_dream_sucess"
            if self.state.get(child_key) is not True:
                # Log moins fréquent
                # self.logger.info(f"⏳ Nightmare attend dream (step {step})") 
                await asyncio.sleep(1)
                return

        # 🔒 Dream attend le nightmare (step précédent)
        if self.role == "dream" and step > 1:
            parent_prev_key = f"depth_step_{step - 1}_nightmare_sucess"
            if self.state.get(parent_prev_key) is not True:
                # self.logger.info(f"⏳ Dream attend nightmare (step {step - 1})")
                await asyncio.sleep(1)
                return

        partition = self.partitions.get(step)
        if not partition:
            return

        self.is_playing = True
        self.logger.info(f"🚀 {self.role.upper()} joue step {step}")

        # On attend la fin de la partition
        success = await self.play_partition(step, partition)

        # Si succès et PAS de reset
        if success:
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


