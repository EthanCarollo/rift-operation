//
//  RobotType.swift
//  swift-sphero-rover
//
//  Created by Tom Boullay on 16/12/2025.
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
