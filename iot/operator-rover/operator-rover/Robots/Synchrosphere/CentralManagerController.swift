//
//  CentralManagerController.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import Pappe
import CoreBluetooth

/// Provides methods and activities to control the bluetooth central manager.
final class CentralManagerController : NSObject, CBCentralManagerDelegate {

    private let context: ControllerContext
    private let centralManager: CBCentralManager
    var peripheral: CBPeripheral?

    init(context: ControllerContext) {
        self.context = context
        centralManager = CBCentralManager(delegate: nil, queue: context.config.queue)
        super.init()
        centralManager.delegate = self
    }
        
    func makeModule(imports: [Module.Import]) -> Module {
        return Module(imports: imports) { name in
                       
            activity (name.ScanForPeripheral_, [name.deviceSelector]) { val in
                exec  {
                    self.context.logInfo("scanning...")
                    self.centralManager.scanForPeripherals(withServices: [.apiService])
                }
                `defer` {
                    self.context.logInfo("stop scanning")
                    self.centralManager.stopScan()
                }
                `await` { self.peripheral != nil && self.peripheral!.matches(val.deviceSelector as SyncsDeviceSelector) }
                exec { self.context.logInfo("got peripheral: \(String(describing: self.peripheral?.name))") }
            }
            
            activity (name.ConnectPeripheral_, []) { val in
                exec {
                    self.context.logInfo("connecting...")
                    guard let peripheral = self.peripheral else { fatalError("peripheral is nil") }
                    self.centralManager.connect(peripheral)
                }
                `await` { self.peripheral?.state == .connected }
            }

            activity (name.DisconnectPeripheral_, []) { val in
                exec {
                    self.context.logInfo("disconnecting...")
                    guard let peripheral = self.peripheral else { fatalError("peripheral is nil") }
                    self.centralManager.cancelPeripheralConnection(peripheral)
                }
                `await` { self.peripheral?.state == .disconnected }
            }
        }
    }
    
    var isBluetoothAvailable: Bool {
        CBManager.authorization.isOk && centralManager.state.isOk
    }
    
    var isPeripheralConnected: Bool {
        peripheral?.state == .connected
    }
    
    func requestDisconnectPeripheral() {
        context.logInfo("request disconnect peripheral")
        guard let peripheral = self.peripheral else { return }
        centralManager.cancelPeripheralConnection(peripheral)
    }
    
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        context.trigger()
    }
    
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        self.context.logInfo("did discover \(peripheral)")
        self.peripheral = peripheral
        context.trigger()
    }
    
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        if peripheral == self.peripheral {
            self.context.logInfo("connected")
            context.trigger()
        }
    }
    
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        if peripheral == self.peripheral {
            context.logInfo("disconnected, reason: \(String(describing: error))")
            context.trigger()
        }
    }
}

private extension SyncsDeviceSelector {
    var namePrefix: String {
        switch self {
        case .anyRVR: return "RV-"
        }
    }
}

private extension CBPeripheral {
    func matches(_ deviceSelector: SyncsDeviceSelector) -> Bool {
        guard let name = name else {
            return false
        }
        // HARDCODED: Only connect to RV-7B4C
        return name == "RV-7B4C"
    }
}

private extension CBManagerAuthorization {
    var isOk: Bool {
        return self == .allowedAlways
    }
}

private extension CBManagerState {
    var isOk: Bool {
        return self == .poweredOn
    }
}
