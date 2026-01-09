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

        self.role = "nightmare"
        
        self.state = {}               # état global reçu du serveur
        self.is_playing = False
        self.device_id = config.device_id

        # Boutons - mapping vers les notes 4, 5, 6
        self.button_pins = self.depthConfig.depth.button_pins
        self.buttons = {
            name: Pin(pin, Pin.IN, Pin.PULL_UP)
            for name, pin in self.button_pins.items()
        }
        
        # Mapping bouton -> note (4-6 pour nightmare)
        self.button_to_note = {
            1: 4,  # Bouton 1 -> FA
            2: 5,  # Bouton 2 -> SOL
            3: 6   # Bouton 3 -> LA
        }
        
        # Mapping note -> son
        self.note_to_sound = {
            4: "FA",
            5: "SOL",
            6: "LA",
        }

        # LED strip (animations JSON)
        self.led_strip = None
        self.led_controller = None
        self.led_anim_mapping = {
            4: "data/depth/nightmare/note1_show.json",
            5: "data/depth/nightmare/note2_show.json",
            6: "data/depth/nightmare/note3_show.json",
        }

        try:
            # Configuration unique de la bande LED
            desired_pin = 15
            desired_count = 19
            
            strip_pin = getattr(self.depthConfig.depth, "led_strip_pin", desired_pin)
            strip_count = getattr(self.depthConfig.depth, "led_strip_count", desired_count)

            self.led_strip = LedStrip(strip_pin, strip_count)
            self.led_strip.clear()

            self.led_controller = FrameworkLedController(self.led_strip)
            
            self.logger.info(
                f"💡 LED strip initialisée (pin={strip_pin}, count={strip_count})"
            )
        except Exception as e:
            self.logger.warning(f"⚠️ LED strip non initialisée : {e}")

    # --------------------------------------------------
    # Helper Functions
    # --------------------------------------------------
    
    def get_role_for_note(self, note):
        """Détermine qui doit jouer cette note"""
        if 1 <= note <= 3:
            return "dream"
        elif 4 <= note <= 6:
            return "nightmare"
        return None
    
    def is_my_turn(self):
        """Vérifie si c'est notre tour de jouer"""
        current_player = self.state.get("depth_current_player")
        partition = self.state.get("depth_partition") or []
        position = self.state.get("depth_partition_position") or 0
        
        if current_player != self.role:
            return False
        
        if position >= len(partition):
            return False
        
        current_note = partition[position]
        expected_role = self.get_role_for_note(current_note)
        
        return expected_role == self.role

    # --------------------------------------------------
    # Conditions métier
    # --------------------------------------------------

    def depth_started(self):
        return self.state.get("rift_part_count") == 2

    def depth_finished(self):
        partition = self.state.get("depth_partition") or []
        position = self.state.get("depth_partition_position") or 0
        return position >= len(partition)

    # --------------------------------------------------
    # Inputs
    # --------------------------------------------------

    async def read_button(self):
        """Lit le bouton pressé et retourne le numéro du bouton (1, 2, ou 3)"""
        for name, button in self.buttons.items():
            if button.value() == 0:
                self.logger.info(f"🔘 Bouton détecté : {name}")
                await asyncio.sleep(0.2)
                return name  # Retourne le nom/numéro du bouton
        return None

    async def play_leds(self, note):
        """Joue l'animation LED correspondant à la note sur la bande unique."""
        if self.state.get("reset_system"):
            return

        if self.led_controller:
            anim_file = self.led_anim_mapping.get(note)
            if anim_file:
                self.logger.info(f"💡 LED Anim Note {note} : {anim_file}")
                
                self.led_controller.play_from_json(anim_file, loop=False)
                
                while self.led_controller.is_playing:
                    if self.state.get("reset_system"):
                        self.led_controller.stop()
                        return
                    
                    self.led_controller.update()
                    await asyncio.sleep(0.02)
                return
        
    async def play_note(self, note):
        note_string = self.note_to_sound.get(note, "FA")
        
        note_json = {"depth_note": note_string}
        
        await self.websocket_client.send(json.dumps(note_json))
        
    async def play_sound(self, name):
        sound_json = {"depth_sound": name}
        
        await self.websocket_client.send(json.dumps(sound_json))

    # --------------------------------------------------
    # Gameplay
    # --------------------------------------------------

    async def play_partition(self):
        """Joue la partie de la partition qui nous revient (ping-pong)"""
        partition = self.state.get("depth_partition") or []
        position = self.state.get("depth_partition_position") or 0
        
        self.logger.info(f"🎮 Starting my turn at position {position}")

        while position < len(partition):
            current_note = partition[position]
            expected_role = self.get_role_for_note(current_note)
            
            # Si ce n'est plus notre tour, on arrête et on passe la main
            if expected_role != self.role:
                self.logger.info(f"🔄 Changement de rôle -> {expected_role}")
                self.state["depth_current_player"] = expected_role
                self.state["depth_partition_position"] = position
                await self.websocket_client.send(json.dumps(self.state))
                return True
            
            # 🛑 Check Reset
            if self.state.get("reset_system"):
                self.logger.info("🔄 Reset demandé - Arrêt partition")
                return False

            # 💡 Allumer la LED pour indiquer quel bouton appuyer
            self.logger.info(f"💡 Indique bouton pour note {current_note}")
            await self.play_leds(current_note)
            
            # Attendre que le joueur appuie sur le bon bouton
            waiting_for_input = True
            while waiting_for_input:
                # 🛑 Check Reset pendant l'attente
                if self.state.get("reset_system"):
                    self.logger.info("🔄 Reset demandé - Arrêt partition")
                    return False
                
                btn = await self.read_button()
                
                if not btn:
                    await asyncio.sleep(0.05)
                    continue

                # Convertir le bouton en note
                pressed_note = self.button_to_note.get(btn)
                
                if pressed_note == current_note:
                    await self.play_note(current_note)
                    self.logger.info(
                        f"✅ Bon bouton : {btn} = note {pressed_note} ({position + 1}/{len(partition)})"
                    )
                    position += 1
                    self.state["depth_partition_position"] = position
                    waiting_for_input = False  # Passer à la note suivante
                else:
                    await self.play_sound("false")
                    self.logger.info(
                        f"❌ Mauvais bouton : {btn} (attendu note {current_note}) → RETRY"
                    )
                    position = 0
                    self.state["depth_partition_position"] = position
                    waiting_for_input = False  # Sortir pour recommencer la boucle

        # Partition terminée !
        await self.play_sound("correct")
        self.state["depth_partition_position"] = position
        await self.websocket_client.send(json.dumps(self.state))
        self.logger.info("🎉 Partition Complete!")
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

        # Check if game is finished
        if self.depth_finished():
            return

        # Check if it's our turn
        if not self.is_my_turn():
            await asyncio.sleep(0.5)
            return

        self.is_playing = True
        self.logger.info(f"🚀 {self.role.upper()} joue!")

        # On attend la fin de la partition
        success = await self.play_partition()

        if success and self.depth_finished():
            self.logger.info("🏁 Depth terminée!")
            self.state["depth_state"] = "complete"
            await self.websocket_client.send(json.dumps(self.state))

        self.is_playing = False
