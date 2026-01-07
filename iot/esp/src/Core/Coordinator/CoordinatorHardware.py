from machine import Pin
try:
    from src.Framework.Button.Button import Button
    from src.Core.Coordinator.CoordinatorButtonDelegate import CoordinatorButtonDelegate
except ImportError:
    pass

class CoordinatorHardware:
    def __init__(self, config, controller):
        self.logger = controller.logger
        self.controller = controller
        self.callback = None
        
        self.button1 = None
        self.button2 = None
        self.button3 = None
        
        # Delegates (instantiated here to be ready, but connected to workshop later)
        self.button1_delegate = CoordinatorButtonDelegate(None, 1)
        self.button2_delegate = CoordinatorButtonDelegate(None, 2)
        self.button3_delegate = CoordinatorButtonDelegate(None, 3)
        
        self.init_hardware()

    def attach_callback(self, callback):
        self.callback = callback
        self.button1_delegate.workshop = callback
        self.button2_delegate.workshop = callback
        self.button3_delegate.workshop = callback

    def update(self):
        pass

    def init_hardware(self):
        self.logger.info("Initializing Coordinator Hardware")
        
        # Button 1 (GPIO 13)
        try:
            self.button1 = Button(pin_id=13, delegate=self.button1_delegate)
            # self.logger.info("Button 1 initialized (13)")
        except Exception as e:
            self.logger.error(f"Button 1 init failed: {e}")

        # Button 2 (GPIO 12)
        try:
            self.button2 = Button(pin_id=12, delegate=self.button2_delegate)
            # self.logger.info("Button 2 initialized (12)")
        except Exception as e:
            self.logger.error(f"Button 2 init failed: {e}")

        # Button 3 (GPIO 14)
        try:
            self.button3 = Button(pin_id=14, delegate=self.button3_delegate)
            # self.logger.info("Button 3 initialized (14)")
        except Exception as e:
            self.logger.error(f"Button 3 init failed: {e}")
            
        # RVR Placeholder (UART) -> We'll add this later fully
        self.logger.info("RVR UART placeholder (TX:17, RX:16)")
