import { RawData } from "ws";
import { Client } from "../../Framework/Server/Client";
import { Server } from "../../Framework/Server/Server";
import Logger from "../../Framework/Utils/Logger";

export class RiftOperationServer extends Server {
  constructor(port: number, state: string = "stranger") {
    super(port)
  }
  
  onConnection(client: Client): void {
    // Execute logics for onConnection, currently useless
  }

  onMessage(client: Client, msg: RawData) {
    try {
      const parsed = JSON.parse(msg.toString());
      this.broadcast(parsed, client);
    } catch {
      Logger.error("Didn't receive JSON on receive message.")
    }
  }
  
  onClose(client: Client): void {
    // Execute logics for onClose, currently useless
  }
}
