import { RawData } from "ws";
import { Client } from "../../Framework/Server/Client";
import ServerState from "./State/ServerState";
import StrangerState from "./State/StrangerState";
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
    const text = msg.toString();
    console.log("[WS IN]", client.id, text);

    // TEMP: relay any JSON message to all other clients (ESP will receive it)
    try {
      const parsed = JSON.parse(text);
      this.broadcast(parsed, client);
      console.log("[WS OUT broadcast]", parsed);
    } catch {
      // ignore non-JSON
    }
    this.state.onMessage(client, text);
  }
  
  onClose(client: Client): void {
    this.state.onClose(client)
  }
}
