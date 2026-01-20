from machine import Pin
try:
    from src.Framework.Button.Button import Button
    from src.Framework.Button.ButtonDelegate import ButtonDelegate
except ImportError:
    raise

import uasyncio as asyncio

class OperatorHardware:
    def __init__(self, controller):
        self.controller = controller
        self.logger = controller.logger
        self.workshop = None
        
        # Hardware components
        self.button = None
        self.led_prompt = None  # Blinks when ready
        self.led_step_1 = None  # Lights up after step 1
        self.led_step_2 = None  # Lights up after step 2
        self.led_step_3 = None  # Lights up after step 3
        
        # Delegates
        self.button_delegate = None
        
        # Blink state
        self.blink_active = False
        self.blink_state = False
        
        self.init_hardware()

    def attach_workshop(self, workshop):
        self.workshop = workshop

    def update(self):
        """Called in main loop for LED blinking"""
        # Blink logic handled by async task
        pass

    def init_hardware(self):
        self.logger.info("Initializing Operator Hardware (Simplified)")

        # 1. Button (GPIO 32)
        try:
            self.button_delegate = OperatorButtonDelegate(self)
            self.button = Button(pin_id=32, delegate=self.button_delegate, debounce_delay=200)
            self.logger.info("Button initialized (GPIO 32)")
        except Exception as e:
            self.logger.error(f"Button init failed: {e}")

        # 2. LED Prompt (GPIO 33) - Blinks
        try:
            self.led_prompt = Pin(33, Pin.OUT)
            self.led_prompt.off()
            self.logger.info("LED Prompt initialized (GPIO 33)")
        except Exception as e:
            self.logger.error(f"LED Prompt init failed: {e}")

        # 3. LED Step 1 (GPIO 14) - Swapped with Step 3 due to wiring
        try:
            self.led_step_1 = Pin(14, Pin.OUT)
            self.led_step_1.off()
            self.logger.info("LED Step 1 initialized (GPIO 14)")
        except Exception as e:
            self.logger.error(f"LED Step 1 init failed: {e}")

        # 4. LED Step 2 (GPIO 26)
        try:
            self.led_step_2 = Pin(26, Pin.OUT)
            self.led_step_2.off()
            self.logger.info("LED Step 2 initialized (GPIO 26)")
        except Exception as e:
            self.logger.error(f"LED Step 2 init failed: {e}")

        # 5. LED Step 3 (GPIO 25) - Swapped with Step 1 due to wiring
        try:
            self.led_step_3 = Pin(25, Pin.OUT)
            self.led_step_3.off()
            self.logger.info("LED Step 3 initialized (GPIO 25)")
        except Exception as e:
            self.logger.error(f"LED Step 3 init failed: {e}")

    def start_blink(self):
        """Start blinking LED Prompt"""
        if not self.blink_active:
            self.blink_active = True
            asyncio.create_task(self._blink_task())

    def stop_blink(self):
        """Stop blinking LED Prompt"""
        self.blink_active = False
        if self.led_prompt:
            self.led_prompt.off()

    async def _blink_task(self):
        """Async task to blink LED Prompt"""
        while self.blink_active:
            if self.led_prompt:
                self.blink_state = not self.blink_state
                if self.blink_state:
                    self.led_prompt.on()
                else:
                    self.led_prompt.off()
            await asyncio.sleep_ms(500)  # Blink every 500ms

    def set_step_led(self, step, state):
        """Turn step LED on/off
        Args:
            step (int): 1, 2, or 3
            state (bool): True = ON, False = OFF
        """
        led = None
        if step == 1:
            led = self.led_step_1
        elif step == 2:
            led = self.led_step_2
        elif step == 3:
            led = self.led_step_3
        
        if led:
            if state:
                led.on()
            else:
                led.off()


class OperatorButtonDelegate(ButtonDelegate):
    def __init__(self, hardware):
        self.hardware = hardware

    def on_click(self):
        if self.hardware.workshop:
            self.hardware.workshop.on_button_press()
