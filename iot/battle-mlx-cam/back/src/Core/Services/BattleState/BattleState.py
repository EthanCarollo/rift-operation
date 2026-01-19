from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...Utils import ProcessingResult
    from ..BattleService import BattleService, BattleRoleState

class BattleState(ABC):
    """Abstract base class for Battle States."""
    
    def __init__(self, service: 'BattleService'):
        self.service = service

    @abstractmethod
    def enter(self):
        """Called when entering the state."""
        pass

    @abstractmethod
    def handle_monitor(self):
        """Called periodically by the monitor loop."""
        pass

    def on_image_task(self, role: str, state: 'BattleRoleState', image_bytes: bytes):
        """
        Full pipeline for processing an image task.
        States can override to do nothing or handle specifically.
        """
        # Default implementation: Do nothing / Log skip
        state.recognition_status = "Skipped (Wrong State)"
        return

    def trigger_attack(self):
        """Handle manual attack trigger."""
        pass
