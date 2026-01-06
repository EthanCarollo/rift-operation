//
//  RobotType.swift
//  coordinator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import Foundation

enum RobotType {
    case rover
    case sphero
    
    func toSynchroSphere() -> SyncsDeviceSelector {
        return switch (self) {
            case .rover:
                .anyRVR
            case .sphero:
                .anyBolt
        }
    }
}
