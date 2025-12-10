import { RawData } from "ws";
import { Client } from "../../Framework/Server/Client";
import ServerState from "./State/ServerState";
import StrangerState from "./State/StrangerState";
import { Server } from "../../Framework/Server/Server";
import Logger from "../../Framework/Utils/Logger";

export class RiftOperationServer extends Server {
  state: ServerState;
  
  constructor(port: number) {
    super(port)
    this.state = new StrangerState(this)
  }

  swapState(state: ServerState){
    this.state = state;
  }
  
  onConnection(client: Client): void {
    this.state.onConnection(client)
  }

  onMessage(client: Client, msg: RawData) {
    try {
      const parsed = JSON.parse(msg.toString());
      this.state.onMessage(client, parsed);
    } catch {
      Logger.error("Didn't receive JSON on receive message.")
    }
  }
  
  onClose(client: Client): void {
    this.state.onClose(client)
  }
}
