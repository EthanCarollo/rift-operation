import * as stackTraceParser from 'stacktrace-parser';
import { WebSocket } from "ws";

export default class Logger {
    static log(message: String){
        console.log(this.constructMessage(message, "log"))
    }

    static warn(message: String){
        console.warn(this.constructMessage(message, "warn"))
    }

    static error(message: String){
        console.error(this.constructMessage(message, "error"))
    }

    private static constructMessage(message: String, level: String): String{
        return level.toUpperCase() + " | " + this.getStack() + " | " + message;
    }

    private static getStack(): String{
        try {
            var error = new Error()
            const stack = stackTraceParser.parse(error.stack!);
            var filename = stack[3].file?.split("/").pop()
            return filename + ":" + stack[3].lineNumber
        } catch (error) {
            return "undefined call file"
        }
    }

    static logConnectionWebSocket(socket: WebSocket){
        try {
            let wrappedSocket = (socket as any)._socket
            const remoteAddress = wrappedSocket.remoteAddress;
            console.log("websocket with ip : " + remoteAddress + " is now connected.")
        } catch(error){
            this.error("WebSocket cannot be logged properly, the socket object may be corrupted.")
        }
    }

    static logCloseWebSocket(socket: WebSocket){
        try {
            let wrappedSocket = (socket as any)._socket
            const remoteAddress = wrappedSocket.remoteAddress;
            console.log("websocket with ip : " + remoteAddress + " just leaved")
        } catch(error){
            this.error("WebSocket cannot be logged properly, the socket object may be corrupted.")
        }
    }
}