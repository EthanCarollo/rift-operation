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
        "DreamSlot1": "XX-XX-XX-XX-XX",  # MFD-1
        "DreamSlot2": "XX-XX-XX-XX-XX",  # MFD-2
        "DreamSlot3": "XX-XX-XX-XX-XX",  # MFD-3
    }
    NIGHTMARE = {
        "NightmareSlot1": "XX-XX-XX-XX-XX",  # MFN-1
        "NightmareSlot2": "XX-XX-XX-XX-XX",  # MFN-2
        "NightmareSlot3": "XX-XX-XX-XX-XX",  # MFN-3
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
