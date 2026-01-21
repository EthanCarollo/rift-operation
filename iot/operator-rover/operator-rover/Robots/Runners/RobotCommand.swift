//
//  RobotCommand.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//


import Foundation

/// All commands that runners can send to the robot.
enum RobotCommand {
    case forward(speed: Int, durationS: Int = 1)
    case backward(speed: Int, durationS: Int = 1)
    case turn(heading: Int, durationS: Int = 1)
    case stop
    case setLED(RobotColor)
    case resetHeading
}
