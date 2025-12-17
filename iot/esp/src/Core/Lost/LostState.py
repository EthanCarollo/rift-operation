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
        """Handle button press (Default: Do nothing)"""
        pass

    async def handle_signal(self, signal):
        """Handle generic signal (e.g. from WS)"""
        pass

    async def next_step(self):
        """Transition to the next state"""
        pass

    async def fast_forward_to(self, target_step):
        """Fast forward to a specific step"""
        if self.step_id >= target_step:
            return

        self.workshop.controller.logger.info("FAST FORWARD -> {}".format(LC.LostSteps.get_name(target_step)))
        
        original_delay = self.workshop.current_step_delay
        self.workshop.current_step_delay = 0
        
        try:
            max_loops = 10
            while self.step_id < target_step and max_loops > 0:
                current_id = self.step_id
                await self.next_step()

                if self.workshop.state.step_id == current_id:
                    break # Stupid loop check
                
                if self.workshop.state.step_id < target_step:
                     await self.workshop.state.fast_forward_to(target_step)
                return # We are done, the recursive chain handles it
        finally:
            self.workshop.current_step_delay = original_delay
