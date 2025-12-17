import Foundation

struct AppConfig {
    static let serverHost = "172.28.55.51"
    static let serverPort = 8000
    static let wsPath = "/ws"
    
    static var websocketURL: URL {
        var components = URLComponents()
        components.scheme = "ws"
        components.host = serverHost
        components.port = serverPort
        components.path = wsPath
        return components.url!
    }
}
