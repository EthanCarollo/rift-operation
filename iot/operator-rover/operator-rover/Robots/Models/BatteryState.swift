//
//  BatteryState.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//


import Foundation

/// Simplified status of the robot's battery.
enum BatteryState {
    case ok
    case low
    case critical
    case unknown
}
