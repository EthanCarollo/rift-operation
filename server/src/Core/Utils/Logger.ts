import { WebSocket } from "ws";

export default class Logger {
    static log(message: String){
        console.log(message)
    }

    static warn(message: String){
        console.warn(message)
    }

    static error(message: String){
        console.error(message)
    }

    static logConnectionWebSocket(socket: WebSocket){
        try {
            let wrappedSocket = (socket as any)._socket
            const remoteAddress = wrappedSocket.remoteAddress;
            this.log(remoteAddress)
        } catch(error){
            this.error("WebSocket cannot be logged properly, the socket object may be corrupted.")
        }
    }

    static logCloseWebSocket(socket: WebSocket){
        try {
            let wrappedSocket = (socket as any)._socket
            const remoteAddress = wrappedSocket.remoteAddress;
            this.log(remoteAddress)
        } catch(error){
            this.error("WebSocket cannot be logged properly, the socket object may be corrupted.")
        }
    }
}