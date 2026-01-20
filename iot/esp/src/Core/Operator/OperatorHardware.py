from machine import Pin, SPI
try:
    from src.Framework.Button.Button import Button
    from src.Framework.Button.ButtonDelegate import ButtonDelegate
    from src.Framework.Rfid.RfidReader import RFIDReader
    from src.Core.Operator.OperatorDelegate import OperatorButtonDelegate, OperatorRfidDelegate
except ImportError:
    # If imports fail, let it crash to see error
    raise

class LedButton:
    def __init__(self, button_pin, led_pin, delegate, name="LedButton", debounce_delay=50):
        self.name = name
        self.led = Pin(led_pin, Pin.OUT)
        self.led.off()
        self.button = Button(pin_id=button_pin, delegate=delegate, debounce_delay=debounce_delay)
        self.is_led_on = False

    def turn_on(self):
        self.led.on()
        self.is_led_on = True

    def turn_off(self):
        self.led.off()
        self.is_led_on = False

class OperatorHardware:
    def __init__(self, controller):
        self.controller = controller
        self.logger = controller.logger
        self.workshop = None

        # Delegates
        self.rift_button_delegate = OperatorButtonDelegate(None, "rift")
        self.battle_button_delegate = OperatorButtonDelegate(None, "battle")
        self.rfid_delegate = OperatorRfidDelegate(None)

        self.rift_button = None
        self.battle_button = None
        self.rfid = None

        self.init_hardware()

    def attach_workshop(self, workshop):
        self.workshop = workshop
        self.rift_button_delegate.workshop = workshop
        self.battle_button_delegate.workshop = workshop
        self.rfid_delegate.workshop = workshop

    def update(self):
        if self.rfid:
            self.rfid.check()

    def init_hardware(self):
        self.logger.info("Initializing Operator Hardware")

        # 1. Rift Button (Left? TBD) - Button + LED
        # Assuming Pins: Btn 32, Led 33 (Example, need to confirm pinout or pick safe ones)
        # User said 4 pins per button. 2 for btn, 2 for led.
        # Let's pick safe pins for ESP32.
        # Rift Button: Btn: 32, Led: 33
        try:
            self.rift_button = LedButton(button_pin=32, led_pin=33, delegate=self.rift_button_delegate, name="RiftButton")
            self.logger.info("Rift Button initialized (Btn:32, Led:33)")
        except Exception as e:
            self.logger.error(f"Rift Button init failed: {e}")

        # 2. Battle Button (Right? TBD) - Button + LED
        # Battle Button: Btn: 25, Led: 26
        try:
            self.battle_button = LedButton(button_pin=25, led_pin=26, delegate=self.battle_button_delegate, name="BattleButton", debounce_delay=200)
            self.logger.info("Battle Button initialized (Btn:25, Led:26, Debounce:200ms)")
        except Exception as e:
            self.logger.error(f"Battle Button init failed: {e}")

        # 3. RFID Reader
        # Standard SPI pins + specific CS/RST
        # SPI2: SCK 18, MOSI 23, MISO 19
        # RST: 4, SDA(CS): 5
        try:
            sck = 18; mosi = 23; miso = 19; cs = 5; rst = 4
            spi = SPI(2, baudrate=2500000, polarity=0, phase=0, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
            self.rfid = RFIDReader(spi, cs, rst, self.rfid_delegate, name="OperatorReader")
            self.logger.info("RFID initialized (SPI2)")
        except Exception as e:
            self.logger.error(f"RFID init failed: {e}")
