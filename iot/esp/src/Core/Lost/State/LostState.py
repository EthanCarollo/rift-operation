"""
LostState.py - Base class for LOST workshop states
"""
import uasyncio as asyncio
import src.Core.Lost.LostConstants as LC

class LostState:
    def __init__(self, workshop):
        self.workshop = workshop
        # Determine step ID based on class name or define in subclass
        self.step_id = None 

    async def enter(self):
        """Called when entering the state"""
        pass

    async def handle_message(self, payload):
        """Handle WebSocket message payload"""
        pass

    async def handle_rfid(self, uid):
        """Handle RFID tag read"""
        pass

    async def handle_button(self):
        """Handle button press"""
        # Default behavior: log and next step
        self.workshop.logger.logger.info(f"BTN action: next_step from {LC.STEP_NAMES.get(self.step_id, 'UNKNOWN')}")
        await asyncio.sleep_ms(self.workshop.current_step_delay)
        await self.next_step()

    async def next_step(self):
        """Transition to the next state"""
        pass
