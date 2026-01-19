from src.Core.Stranger.State.StrangerControllerState import StrangerControllerState
import asyncio

class StrangerRecognizedState(StrangerControllerState):
    def __init__(self, controller):
        super().__init__(controller)
        self.send_state("recognized")
        self.controller.logger.debug("Stranger recognized! Sleeping 5s before inactive...")
        asyncio.create_task(self.auto_transition())

    async def auto_transition(self):
        await asyncio.sleep(5)
        self.controller.logger.debug("5s elapsed. Transitioning to Inactive.")
        from src.Core.Stranger.State.StrangerInactiveState import StrangerInactiveState
        self.controller.swap_state(StrangerInactiveState(self.controller))

    def update(self):
        pass
