"""
RiftConstants.py - Configuration for the RIFT workshop
"""

class RiftSteps:
    IDLE = 0
    STEP_1 = 1
    STEP_2 = 2
    STEP_3 = 3
    DONE = 4

    _NAMES = {
        IDLE: "0: IDLE",
        STEP_1: "1: STEP_1",
        STEP_2: "2: STEP_2",
        STEP_3: "3: STEP_3",
        DONE: "4: DONE"
    }

    @classmethod
    def get_name(cls, step_id):
        return cls._NAMES.get(step_id, str(step_id))

class RiftTags:
    """Expected RFID UIDs for each slot"""
    DREAM = {
        "DreamSlot1": "AF-41-2B-1C-D9",  # MFD-1 a remplacer par le tag correct
        "DreamSlot2": "9F-F8-46-1C-3D",  # MFD-2
        "DreamSlot3": "F3-3B-50-AC-34",  # MFD-3
    }
    NIGHTMARE = {
        "NightmareSlot1": "AF-41-2B-1C-D9",  # MFN-1
        "NightmareSlot2": "D3-67-36-AC-2E",  # MFN-2
        "NightmareSlot3": "53-66-92-AA-0D",  # MFN-3
    }
    # Helper methods
    @staticmethod
    def get_all_tags():
        tags = {}
        tags.update(RiftTags.DREAM)
        tags.update(RiftTags.NIGHTMARE)
        return tags
    
    @staticmethod
    def is_dream_slot(slot_name):
        return slot_name.startswith("Dream")
    
    @staticmethod
    def is_nightmare_slot(slot_name):
        return slot_name.startswith("Nightmare")
