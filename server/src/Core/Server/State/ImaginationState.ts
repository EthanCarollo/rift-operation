import Logger from "../../../Framework/Utils/Logger";
import { Client } from "../../../Framework/Server/Client";
import ServerState from "./ServerState";

/**
 * Imagination State is the third state
 * 
 * Responsability of : Tom
 */
export default class ImaginationState extends ServerState {
    public onConnection(client: Client): void {
        Logger.error("Not already implemented")
    }

    public onMessage(client: Client, message: JSON): void {
        this.server.broadcast(message, client);
        Logger.log("[WS OUT broadcast] " + message);
    }

    public onClose(client: Client): void {
        Logger.error("Not already implemented")
    }
}