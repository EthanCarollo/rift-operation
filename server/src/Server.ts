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
      });
    });
  }

  broadcast(message: any, exclude?: Client) {
    for (const client of this.clients) {
      if (client !== exclude) client.send(message);
    }
  }
}
