import ujson as json
from machine import Pin
import time
from src.Framework.EspController import EspController

class DepthController(EspController):
    def __init__(self, config):
        super().__init__(config)
        self.logger.name = "DepthController"

        # Depth-specific components
        self.role = config.depth.role
        self.buttons = {n: Pin(p, Pin.IN, Pin.PULL_UP) for n, p in config.depth.button_pins.items()}
        
        if self.role == "parent":
            self.leds = {n: Pin(p, Pin.OUT) for n, p in config.depth.led_pins.items()}
        else:
            self.leds = None
        
        self.current_partition = None
        self.partitions = config.depth.partitions

    def depth_active(self):
        """Check if depth experience is active based on state"""
        return (
            self.websocket_client.state.get("preset_depth") is True and
            (self.websocket_client.state.get("children_rift_part_count", 0) +
             self.websocket_client.state.get("parent_rift_part_count", 0)) == 2
        )
    
    def determine_step(self):
        """Determine current step based on state"""
        for i in (1, 2, 3):
            if self.role == "child":
                if self.websocket_client.state.get(f"step_{i}_enfant_sucess") is None:
                    return i
            else:
                if self.websocket_client.state.get(f"step_{i}_parent_sucess") is None:
                    return i
        return None
    
    def read_button(self):
        """Read button press with debounce"""
        for n, b in self.buttons.items():
            if b.value() == 0:
                self.logger.debug(f"Button {n} pressed")
                time.sleep(0.2)  # debounce
                return n
        return None
    
    def show_leds(self, part):
        """Show LED sequence for parent role"""
        if self.role != "parent" or not self.leds:
            return
        
        self.logger.info(f"LED sequence: {part}")
        for n in part:
            self.logger.debug(f"LED {n} ON")
            self.leds[n].value(1)
            time.sleep(0.4)
            self.logger.debug(f"LED {n} OFF")
            self.leds[n].value(0)
            time.sleep(0.2)
    
    def play_child(self, part):
        """Child gameplay logic"""
        idx = 0
        self.logger.info(f"Child playing: {part}")
        while idx < len(part):
            btn = self.read_button()
            if btn:
                if btn == part[idx]:
                    self.logger.debug(f"OK - button {btn}")
                    idx += 1
                else:
                    self.logger.debug(f"Wrong button {btn}, expected {part[idx]} - reset")
                    idx = 0
            time.sleep(0.01)
        return True
    
    def play_parent(self, part):
        """Parent gameplay logic"""
        self.show_leds(part)
        idx = 0
        self.logger.info(f"Parent playing: {part}")
        while idx < len(part):
            btn = self.read_button()
            if btn:
                if btn == part[idx]:
                    self.logger.debug(f"OK - button {btn}")
                    idx += 1
                else:
                    self.logger.debug(f"Wrong button {btn}, expected {part[idx]} - reset")
                    idx = 0
            time.sleep(0.01)
        return True
    
    async def process_message(self, message):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            self.logger.info(f"Received message: {data}")
            self.websocket_client.merge_state(data)
            
            # Handle specific message types
            if data.get("type") == "partition":
                self.current_partition = list(map(int, data["value"].split(",")))
                self.logger.info(f"New partition: {self.current_partition}")
            
            elif data.get("type") == "unlock":
                self.logger.info("⚡ FINAL ACTION ⚡")
                
        except Exception as e:
            self.logger.error(f"Failed to parse message: {message}, error: {e}")
    
    async def execute_partition(self):
        """Execute current partition if available"""
        if self.current_partition:
            if self.role == "child":
                ok = self.play_child(self.current_partition)
            else:
                ok = self.play_parent(self.current_partition)
            
            if ok:
                self.logger.info("Partition successful → sending success")
                await self.websocket_client.send(json.dumps({"type": "message", "value": "success"}))
                self.current_partition = None
    
    async def depth_game_logic(self):
        """Depth-specific game logic"""
        if not self.depth_active():
            return
        
        step = self.determine_step()
        if step is None:
            return
        
        if self.role == "child":
            key = f"step_{step}_enfant_sucess"
        else:
            key = f"step_{step}_parent_sucess"
        
        # For parent, only play after child success
        if self.role == "parent":
            child_key = f"step_{step}_enfant_sucess"
            if self.websocket_client.state.get(child_key) is not True:
                return
        
        if self.websocket_client.state.get(key) is None:
            self.logger.info(f"{self.role.capitalize()} playing step {step}")
            partition = self.partitions.get(step, [])
            if self.play_child(partition) if self.role == "child" else self.play_parent(partition):
                self.websocket_client.send_state(key, True)
                self.websocket_client.state[key] = True
    
    async def main(self):
        self.logger.info("Starting EspController main loop")
        
        if not self.wifi_manager.connect():
            self.logger.error("Failed to connect to WiFi")
            return
        
        self.logger.info("WiFi connected successfully")
        
        if not await self.websocket_client.connect():
            self.logger.error("Failed to connect to WebSocket")
            return
        
        self.logger.info("WebSocket connected successfully")
        
        # Send registration
        register_msg = json.dumps({"type": "register", "value": self.role})
        await self.websocket_client.send(register_msg)
        
        listener_task = asyncio.create_task(
            self.websocket_client.listen(self.process_message)
        )
        
        counter = 0
        while True:
            await asyncio.sleep(self.config.heartbeat_interval)
            counter += 1
            
            # Execute partition if available
            await self.execute_partition()
            
            # Execute depth game logic
            await self.depth_game_logic()
            
            # Send heartbeat
            heartbeat_message = json.dumps({
                "type": "heartbeat", 
                "counter": counter,
                "device_id": self.config.device_id,
                "role": self.role
            })
            
            await self.websocket_client.send(heartbeat_message)
            self.logger.debug(f"Sent heartbeat: {counter}")
    
    def cleanup(self):
        self.logger.info("Cleaning up resources")
        self.websocket_client.close()
        self.wifi_manager.disconnect()
        self.logger.info("Cleanup completed")