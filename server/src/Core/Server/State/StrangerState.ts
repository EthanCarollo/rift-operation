import Logger from "../../Utils/Logger";
import { Client } from "../../../Framework/Server/Client";
import ServerState from "./ServerState";

export default class StrangerState extends ServerState {
    public onConnection(client: Client): void {
        Logger.error("Not already implemented")
    }

    public onMessage(client: Client, message: String): void {
        Logger.error("Not already implemented")
    }

    public onClose(client: Client): void {
        Logger.error("Not already implemented")
    }
}