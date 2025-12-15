import ujson

class RiftOperationJsonData:
    def __init__(self, 
                children_rift_part_count=None, 
                parent_rift_part_count=None, 
                start_system=None, 
                recognized_stranger_name=None, 
                pinguin_micro=None, pinguin_audio=None,
                depth_step_1_parent_sucess=None, 
                depth_step_2_parent_sucess=None, 
                depth_step_3_parent_sucess=None, 
                depth_step_1_enfant_sucess=None, 
                depth_step_2_enfant_sucess=None, 
                depth_step_3_enfant_sucess=None, 
                torch_scanned=None, 
                cage_is_on_monster=None, 
                preset_stranger=None, 
                preset_depth=None, 
                preset_lost=None, 
                preset_ending=None):
        self.children_rift_part_count = children_rift_part_count
        self.parent_rift_part_count = parent_rift_part_count
        self.start_system = start_system
        self.recognized_stranger_name = recognized_stranger_name
        self.pinguin_micro = pinguin_micro
        self.pinguin_audio = pinguin_audio
        self.depth_step_1_parent_sucess = depth_step_1_parent_sucess
        self.depth_step_2_parent_sucess = depth_step_2_parent_sucess
        self.depth_step_3_parent_sucess = depth_step_3_parent_sucess
        self.depth_step_1_enfant_sucess = depth_step_1_enfant_sucess
        self.depth_step_2_enfant_sucess = depth_step_2_enfant_sucess
        self.depth_step_3_enfant_sucess = depth_step_3_enfant_sucess
        self.torch_scanned = torch_scanned
        self.cage_is_on_monster = cage_is_on_monster
        self.preset_stranger = preset_stranger
        self.preset_depth = preset_depth
        self.preset_lost = preset_lost
        self.preset_ending = preset_ending

    def to_json(self):
        return ujson.dumps(self.__dict__)
