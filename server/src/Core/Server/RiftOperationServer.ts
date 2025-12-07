import { WebSocketServer, WebSocket, RawData } from "ws";
import { Client } from "../../Framework/Server/Client";
import ServerState from "./State/ServerState";
import StrangerState from "./State/StrangerState";
import Logger from "../Utils/Logger";
import JsonFactory from "../Utils/Json/JsonFactory";
import { Server } from "../../Framework/Server/Server";

export class RiftOperationServer extends Server {
  state: ServerState;
  
  constructor(port: number) {
    super(port)
    this.state = new StrangerState(this)
  }
  
  onConnection(client: Client): void {
    this.state.onConnection(client)
  }

  onMessage(client: Client, msg: RawData) {
    this.state.onMessage(client, msg.toString())
  }
  
  onClose(client: Client): void {
    this.state.onClose(client)
  }
}
