import { Client } from "./Client";
import { Server } from "./Server";

export interface Command {
  type: string;
  payload?: any;
}

export class CommandHandler {
  server: Server;

  constructor(server: Server) {
    this.server = server;
  }

  handle(client: Client, command: Command) {
    switch (command.type) {
      case "echo":
        client.send({ type: "echo", payload: command.payload });
        break;

      case "broadcast":
        this.server.broadcast({ type: "message", from: client.id, payload: command.payload }, client);
        break;

      case "ping":
        client.send({ type: "pong", time: Date.now() });
        break;

      case "register":
        client.send({ type: "registered", id: client.id });
        break;

      default:
        client.send({ type: "error", message: "unknown_command" });
    }
  }
}
