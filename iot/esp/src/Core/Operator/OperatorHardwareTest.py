
import utime
import gc
from src.Framework.Logger import Logger
from src.Core.Operator.OperatorHardware import OperatorHardware

# Mock Controller to provide logger
class TestController:
    def __init__(self):
        self.logger = Logger("HardwareTest")
        self.config = None

# Mock Workshop to handle events
class TestWorkshop:
    def __init__(self, hardware):
        self.hardware = hardware
        self.logger = Logger("TestWorkshop")

    def on_button_press(self, button_type):
        self.logger.info(f"Button Pressed: {button_type}")
        
        # Logic: Toggle LED
        target_button = None
        if button_type == "rift":
            target_button = self.hardware.rift_button
        elif button_type == "battle":
            target_button = self.hardware.battle_button
            
        if target_button:
            if target_button.is_led_on:
                self.logger.info(f"Turning OFF {button_type} LED")
                target_button.turn_off()
            else:
                self.logger.info(f"Turning ON {button_type} LED")
                target_button.turn_on()

    def on_rfid_read(self, uid):
        self.logger.info(f"RFID TAG DETECTED -> UUID: {uid}")
        print(f"!!! COPY THIS UUID: {uid} !!!")

# Main Test Loop
def run_test():
    print("--- STARTING HARDWARE TEST ---")
    
    # 1. Setup
    controller = TestController()
    hardware = OperatorHardware(controller)
    workshop = TestWorkshop(hardware)
    hardware.attach_workshop(workshop)
    
    print("Hardware Initialized.")
    print(" - Press Buttons to toggle LEDs.")
    print(" - Scan RFID to see UUID.")
    print("------------------------------")
    
    # 2. Loop
    while True:
        try:
            hardware.update()
            utime.sleep_ms(20) # 50Hz update
        except KeyboardInterrupt:
            print("Test Stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            utime.sleep(1)

if __name__ == "__main__":
    run_test()
