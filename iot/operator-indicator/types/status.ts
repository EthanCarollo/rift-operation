// Status payload interface
export interface OperatorStatus {
    device_id: string
    rift_part_count: number | null
    depth_partition_position: number | null
    battle_boss_hp: number | null
    stranger_state: string | null
    depth_state: string | null // New field for World 2
    battle_state: string | null
    battle_drawing_dream_recognised: boolean | null
    battle_drawing_nightmare_recognised: boolean | null
    battle_hit_confirmed: boolean | null
    start_system: boolean
    operator_launch_close_rift_step_1: boolean | null
    operator_launch_close_rift_step_2: boolean | null
    operator_launch_close_rift_step_3: boolean | null
    reset_system: boolean | null
    [key: string]: any // Allow additional properties
}
