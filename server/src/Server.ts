import { WebSocketServer } from "ws";
import { Client } from "./Client";
import {Command, CommandHandler} from "./CommandHandler";

export class Server {
  wss: WebSocketServer;
  clients: Set<Client>;
  commands: CommandHandler;

  constructor(port: number) {
    this.wss = new WebSocketServer({ port });
    this.clients = new Set();
    this.commands = new CommandHandler(this);

    this.wss.on("connection", (socket) => {
      const client = new Client(socket);
      this.clients.add(client);

      // Log client connection with id and remote address when available
      const remoteAddress = (socket as any)._socket && (socket as any)._socket.remoteAddress
        ? (socket as any)._socket.remoteAddress
        : undefined;
      console.log(`Client connected: id=${client.id}${remoteAddress ? ` remote=${remoteAddress}` : ""}`);

      client.send({ type: "welcome", id: client.id, time: Date.now() });

      socket.on("message", (msg) => {
        try {
          const command: Command = JSON.parse(msg.toString());
          this.commands.handle(client, command);
        } catch {
          client.send({ type: "error", message: "invalid_json" });
        }
      });

      socket.on("close", () => {
        this.clients.delete(client);
        // Log client disconnection
        console.log(`Client disconnected: id=${client.id}${remoteAddress ? ` remote=${remoteAddress}` : ""}`);
      });
    });
  }

  broadcast(message: any, exclude?: Client) {
    for (const client of this.clients) {
      if (client !== exclude) client.send(message);
    }
  }
}
