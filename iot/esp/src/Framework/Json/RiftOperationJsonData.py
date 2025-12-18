import ujson

class RiftOperationJsonData:
    def __init__(self, 
                device_id,
                dream_rift_part_count=None, 
                nightmare_rift_part_count=None, 
                
                start_system=None, 
                stranger_state=None,
                recognized_stranger_name=None, 
                pinguin_micro=None, 
                pinguin_audio=None,
                
                depth_state=None,
                depth_step_1_nightmare_sucess=None, 
                depth_step_2_nightmare_sucess=None, 
                depth_step_3_nightmare_sucess=None, 
                depth_step_1_dream_sucess=None, 
                depth_step_2_dream_sucess=None, 
                depth_step_3_dream_sucess=None, 

                lost_state=None,
                torch_scanned=None, 
                cage_is_on_monster=None, 

                end_system=None,
                
                preset_stranger=None, 
                preset_depth=None, 
                preset_imagination=None, 
                preset_ending=None):
        
        if device_id is None:
            raise ValueError("device_id is mandatory")
            
        self.device_id = device_id
        self.dream_rift_part_count = dream_rift_part_count
        self.nightmare_rift_part_count = nightmare_rift_part_count
        
        self.start_system = start_system
        self.stranger_state = stranger_state
        self.recognized_stranger_name = recognized_stranger_name
        self.pinguin_micro = pinguin_micro
        self.pinguin_audio = pinguin_audio
        
        self.depth_state = depth_state
        self.depth_step_1_nightmare_sucess = depth_step_1_nightmare_sucess
        self.depth_step_2_nightmare_sucess = depth_step_2_nightmare_sucess
        self.depth_step_3_nightmare_sucess = depth_step_3_nightmare_sucess
        self.depth_step_1_dream_sucess = depth_step_1_dream_sucess
        self.depth_step_2_dream_sucess = depth_step_2_dream_sucess
        self.depth_step_3_dream_sucess = depth_step_3_dream_sucess
        
        self.lost_state = lost_state
        self.torch_scanned = torch_scanned
        self.cage_is_on_monster = cage_is_on_monster
        
        self.end_system = end_system

        self.preset_stranger = preset_stranger
        self.preset_depth = preset_depth
        self.preset_imagination = preset_imagination
        self.preset_ending = preset_ending

    def to_json(self):
        return ujson.dumps(self.__dict__)
