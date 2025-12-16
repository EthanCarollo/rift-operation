//
//  BatteryState.swift
//  swift-sphero-rover
//
//  Created by Tom Boullay on 16/12/2025.
//


import Foundation

/// Simplified status of the robot's battery.
enum BatteryState {
    case ok
    case low
    case critical
    case unknown
}
