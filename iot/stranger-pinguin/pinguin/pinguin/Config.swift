import Foundation

enum ServerMode: String, CaseIterable, Identifiable {
    case cosmo = "Cosmo"
    case darkCosmo = "Dark Cosmo"
    
    var id: String { rawValue }
    
    var port: Int {
        switch self {
        case .cosmo: return 8000
        case .darkCosmo: return 8001
        }
    }
    
    var displayName: String { rawValue }
}

struct AppConfig {
    static let serverHost = "192.168.10.5"
    static let wsPath = "/ws"
    
    static func websocketURL(for mode: ServerMode) -> URL {
        var components = URLComponents()
        components.scheme = "ws"
        components.host = serverHost
        components.port = mode.port
        components.path = wsPath
        return components.url!
    }
    
    static func httpURL(for mode: ServerMode) -> URL {
        var components = URLComponents()
        components.scheme = "http"
        components.host = serverHost
        components.port = mode.port
        components.path = ""
        return components.url!
    }
    
    // Legacy support - default to cosmo
    static var websocketURL: URL {
        websocketURL(for: .cosmo)
    }
    
    static var httpURL: URL {
        httpURL(for: .cosmo)
    }
}

