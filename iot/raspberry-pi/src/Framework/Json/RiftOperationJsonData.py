import json

class RiftOperationJsonData:
    def __init__(self, 
                device_id,
                rift_part_count=None,
                start_system=None,
                
                operator_launch_close_rift_step_1=None,
                operator_launch_close_rift_step_2=None,
                operator_launch_close_rift_step_3=None,
                operator_start_system=None,
                
                stranger_state=None,
                stranger_recognized_name=None,
                
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
                lost_cage_is_on_monster=None, 
                lost_light_is_triggered=None,
                lost_drawing_light_recognized=None,
                lost_mp3_play=None,
                lost_video_play=None,

                battle_state=None,
                battle_drawing_dream_recognised=None,
                battle_drawing_nightmare_recognised=None,
                battle_hit_confirmed=None,
                battle_cage_nightmare=None,
                battle_cage_dream=None,
                battle_video_play=None,
                battle_music_play=None,

                end_system=None,
                reset_system=None):
        
        if device_id is None:
            raise ValueError("device_id is mandatory")
            
        self.device_id = device_id
        self.rift_part_count = rift_part_count
        self.start_system = start_system
        
        self.operator_launch_close_rift_step_1 = operator_launch_close_rift_step_1
        self.operator_launch_close_rift_step_2 = operator_launch_close_rift_step_2
        self.operator_launch_close_rift_step_3 = operator_launch_close_rift_step_3
        self.operator_start_system = operator_start_system
        
        self.stranger_state = stranger_state
        self.stranger_recognized_name = stranger_recognized_name
        
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
        self.lost_cage_is_on_monster = lost_cage_is_on_monster
        self.lost_light_is_triggered = lost_light_is_triggered
        self.lost_drawing_light_recognized = lost_drawing_light_recognized
        self.lost_mp3_play = lost_mp3_play
        self.lost_video_play = lost_video_play

        self.battle_state = battle_state
        self.battle_drawing_dream_recognised = battle_drawing_dream_recognised
        self.battle_drawing_nightmare_recognised = battle_drawing_nightmare_recognised
        self.battle_hit_confirmed = battle_hit_confirmed
        self.battle_cage_nightmare = battle_cage_nightmare
        self.battle_cage_dream = battle_cage_dream
        self.battle_video_play = battle_video_play
        self.battle_music_play = battle_music_play
        
        self.end_system = end_system
        self.reset_system = reset_system

    def to_json(self):
        return json.dumps(self.__dict__)


