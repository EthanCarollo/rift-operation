import Logger from "../../../Framework/Utils/Logger";
import { Client } from "../../../Framework/Server/Client";
import ServerState from "./ServerState";

/**
 * Imagination State is the secondary state
 * 
 * Responsability of : Anthony
 */
export default class DepthState extends ServerState {
    public onConnection(client: Client): void {
        Logger.error("Not already implemented")
    }

    public onMessage(client: Client, message: JSON): void {
        Logger.error("Not already implemented")
    }

    public onClose(client: Client): void {
        Logger.error("Not already implemented")
    }
}