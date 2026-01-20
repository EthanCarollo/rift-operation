
import uasyncio as asyncio
import ujson as json

class OperatorWorkshop:
    def __init__(self, controller):
        self.controller = controller
        self.logger = controller.logger
        self.hardware = None
        self._last_payload = {}
        
        # Rift Step Tracking
        self.current_step = 0  # 0 = idle, 1/2/3 = waiting for button press
        self.current_rift_part_count = 0

    def attach_hardware(self, hardware):
        self.hardware = hardware
        self.hardware.attach_workshop(self)

    # --- Hardware Events ---
    def on_button_press(self):
        """Called when button is pressed"""
        self.logger.info(f"Button Pressed - Step {self.current_step}")
        
        if self.current_step > 0:
            asyncio.create_task(self.handle_button_press())

    async def handle_button_press(self):
        """Handle button press and send WebSocket payload"""
        if self.current_step == 0:
            return  # Button not active
        
        # Stop blinking
        if self.hardware:
            self.hardware.stop_blink()
        
        # Construct payload
        payload_key = f"operator_launch_close_rift_step_{self.current_step}"
        update = {
            "device_id": self.controller.config.device_id,
            "rift_part_count": self.current_rift_part_count,
            payload_key: True
        }
        
        # Send WebSocket
        await self.send_json(update)
        
        # Light up corresponding step LED
        if self.hardware:
            self.hardware.set_step_led(self.current_step, True)
        
        # Reset current step
        self.current_step = 0

    # --- WebSocket Handling ---
    async def process_message(self, message: str):
        try:
            data = json.loads(message)
            payload = data.get("value", data) if isinstance(data, dict) else data
        except Exception:
            return

        if not isinstance(payload, dict):
            return

        self._last_payload = payload
        
        # Global Reset
        if payload.get("reset_system") is True:
            await self.reset()
            return

        # Check rift part count for step activation
        await self.check_rift_status(payload)

    async def check_rift_status(self, payload):
        """Check if we need to activate button for rift closure"""
        count = payload.get("rift_part_count", 0)
        self.current_rift_part_count = count
        
        # Determine which step to trigger
        step_to_trigger = 0
        if count == 2:
            step_to_trigger = 1
        elif count == 4:
            step_to_trigger = 2
        elif count == 6:
            step_to_trigger = 3
        
        if step_to_trigger > 0:
            # Check if this step is already done
            done_key = f"operator_launch_close_rift_step_{step_to_trigger}"
            is_done = payload.get(done_key, False)
            
            if not is_done and self.current_step == 0:
                # Activate button for this step
                self.current_step = step_to_trigger
                self.logger.info(f"Ready for Step {step_to_trigger} - LED Blinking")
                
                if self.hardware:
                    self.hardware.start_blink()
            
            elif is_done and self.current_step == step_to_trigger:
                # Step completed, deactivate
                self.current_step = 0
                if self.hardware:
                    self.hardware.stop_blink()

    async def send_json(self, updates=None):
        """Send JSON payload via WebSocket"""
        payload = {}
        
        if updates:
            payload.update(updates)
        else:
            payload = dict(self._last_payload)
            payload["device_id"] = self.controller.config.device_id
            
        try:
            await self.controller.websocket_client.send(json.dumps(payload))
            self.logger.info(f"Sent: {updates}")
        except Exception as e:
            self.logger.error(f"Send failed: {e}")

    async def reset(self):
        """Reset all state"""
        self.logger.info("System Reset")
        self.current_step = 0
        self.current_rift_part_count = 0
        
        if self.hardware:
            self.hardware.stop_blink()
            self.hardware.set_step_led(1, False)
            self.hardware.set_step_led(2, False)
            self.hardware.set_step_led(3, False)
