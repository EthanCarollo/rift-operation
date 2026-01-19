from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...Core.Utils import ProcessingResult
    from ..BattleService import BattleService

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

    def process_frame(self, role: str, image_bytes: bytes) -> Optional['ProcessingResult']:
        """
        Process a frame. Default behavior delegates to service.processor.
        """
        # Default behavior: Process via ImageProcessor
        result = self.service.processor.process_frame(image_bytes, self.service.current_attack)
        return result
    
    def trigger_attack(self):
        """Handle manual attack trigger."""
        pass
