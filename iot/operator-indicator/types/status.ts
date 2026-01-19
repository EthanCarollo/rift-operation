// Status payload interface
export interface OperatorStatus {
    device_id: string
    rift_part_count: number | null
    depth_partition_position: number | null
    battle_boss_hp: number | null
    stranger_state: string | null
    start_system: boolean
    operator_launch_close_rift_step_1: boolean | null
    [key: string]: any // Allow additional properties
}
