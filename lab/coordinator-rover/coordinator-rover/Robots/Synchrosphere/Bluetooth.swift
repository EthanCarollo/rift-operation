//
//  Bluetooth.swift
//  coordinator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import CoreBluetooth

extension CBUUID {
    
    // MARK: Services
    
    static let apiService = CBUUID(string: "00010001-574f-4f20-5370-6865726f2121")
    static let antiDosService = CBUUID(string: "00020001-574F-4F20-5370-6865726F2121")

    // MARK: Characteristics
    
    static let apiCharacteristic = CBUUID(string: "00010002-574f-4f20-5370-6865726f2121")
    static let antiDoSCharacteristic = CBUUID(string: "00020005-574f-4f20-5370-6865726f2121")
}
