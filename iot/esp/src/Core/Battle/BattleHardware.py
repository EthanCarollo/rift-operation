"""
BattleHardware.py - Hardware wrapper for BATTLE workshop
Manages: LED Strip, RFID Reader, Arcade Button with LED
"""
from machine import SPI, Pin
import uasyncio as asyncio

try:
    from src.Framework.Led.LedStrip import LedStrip
    from src.Framework.Rfid.RfidReader import RFIDReader
    from src.Framework.Button.Button import Button
    
    from src.Core.Battle.BattleRfidDelegate import BattleRfidDelegate
    from src.Core.Battle.BattleButtonDelegate import BattleButtonDelegate
except ImportError:
    pass


class BattleHardware:
    def __init__(self, config, controller, role):
        """
        Initialize hardware for Battle workshop.
        
        :param config: Controller config
        :param controller: Parent controller
        :param role: "parent" or "child"
        """
        self.role = role
        self.logger = controller.logger
        self.controller = controller
        self.callback = None
        
        # Hardware components
        self.led_strip = None
        self.rfid = None
        self.button = None
        self.button_led_pin = None
        
        # Delegates
        self.rfid_delegate = BattleRfidDelegate(None)
        self.button_delegate = BattleButtonDelegate(None)
        
        self.init_hardware()

    def attach_callback(self, callback):
        """Attach workshop for callbacks"""
        self.callback = callback
        self.rfid_delegate.workshop = callback
        self.button_delegate.workshop = callback

    def init_hardware(self):
        """Initialize all hardware based on role"""
        self.logger.info(f"[BattleHardware] Initializing for role: {self.role}")
        
        if self.role == "parent":
            # Parent ESP: LED Strip (pin 27), RFID (SPI), Button (pin 26), Button LED (pin 25)
            self._init_led_strip(pin=27, num_leds=30)
            self._init_button(button_pin=26, led_pin=25)
            self._init_rfid(sck=18, mosi=17, miso=19, cs=5, rst=21)
            
        elif self.role == "child":
            # Child ESP: LED Strip (pin 27), RFID (SPI), Button (pin 26), Button LED (pin 25)
            self._init_led_strip(pin=27, num_leds=30)
            self._init_button(button_pin=26, led_pin=25)
            self._init_rfid(sck=18, mosi=17, miso=19, cs=5, rst=21)

    def _init_led_strip(self, pin, num_leds):
        """Initialize WS2812B LED strip"""
        try:
            self.led_strip = LedStrip(pin_id=pin, num_pixels=num_leds)
            self.logger.info(f"[BattleHardware] LED Strip initialized (pin {pin}, {num_leds} LEDs)")
        except Exception as e:
            self.logger.error(f"[BattleHardware] LED Strip init failed: {e}")

    def _init_button(self, button_pin, led_pin):
        """Initialize arcade button with integrated LED"""
        try:
            self.button = Button(pin_id=button_pin, delegate=self.button_delegate)
            self.button_led_pin = Pin(led_pin, Pin.OUT)
            self.button_led_pin.off()
            self.logger.info(f"[BattleHardware] Button initialized (btn:{button_pin}, led:{led_pin})")
        except Exception as e:
            self.logger.error(f"[BattleHardware] Button init failed: {e}")

    def _init_rfid(self, sck, mosi, miso, cs, rst):
        """Initialize RFID reader"""
        try:
            spi = SPI(2, baudrate=2500000, polarity=0, phase=0,
                     sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
            self.rfid = RFIDReader(spi, cs, rst, self.rfid_delegate, name=f"BattleRFID_{self.role}")
            self.logger.info(f"[BattleHardware] RFID initialized")
        except Exception as e:
            self.logger.error(f"[BattleHardware] RFID init failed: {e}")

    def update(self):
        """Main update loop - called by controller"""
        if self.rfid:
            self.rfid.check()

    # --- LED Strip Methods ---
    
    def set_led_color(self, color):
        """Set all LEDs to a solid color"""
        if self.led_strip:
            self.led_strip.stop_effect()
            self.led_strip.fill(color)
            self.led_strip.show()

    def clear_leds(self):
        """Turn off all LEDs"""
        if self.led_strip:
            self.led_strip.stop_effect()
            self.led_strip.clear()

    async def blink_leds(self, color, on_ms, off_ms):
        """Start blinking effect on LEDs"""
        if self.led_strip:
            await self.led_strip.blink(color, on_ms, off_ms)

    def stop_led_effect(self):
        """Stop any running LED effect"""
        if self.led_strip:
            self.led_strip.stop_effect()

    # --- Arcade Button LED Methods ---
    
    def set_button_led(self, on):
        """Turn button LED on or off"""
        if self.button_led_pin:
            if on:
                self.button_led_pin.on()
            else:
                self.button_led_pin.off()
