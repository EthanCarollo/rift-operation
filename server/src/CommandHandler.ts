import { Server } from "./Server";
import { Client } from "./Client";
import { ExperienceManager } from "./ExperienceManager";

export interface Command {
  type: string;
  payload?: any;
  value?: any;
}

export class CommandHandler {
  private server: Server;
  private manager: ExperienceManager;

  constructor(server: Server) {
    this.server = server;
    this.manager = new ExperienceManager(server);
    this.manager.start("depth"); // expérience par défaut
  }

  handle(client: Client, command: Command) {
    const payload = command.payload ?? command.value;

    switch (command.type) {
      // -----------------------------
      // NEW EXPERIENCE SYSTEM
      // -----------------------------
      case "select_experience":
        console.log("Switching experience to:", payload);
        this.manager.start(payload);
        break;

      // -----------------------------
      // OLD PROTOCOL SUPPORT
      // -----------------------------
      case "echo":
        client.send({ type: "echo", payload });
        break;

      case "broadcast":
        this.server.broadcast(
          { type: "message", from: client.id, payload },
          client
        );
        break;

      case "ping":
        client.send({ type: "pong", time: Date.now() });
        break;

      case "button":
        console.log(`Button event from ${client.id}:`, payload);
        this.server.broadcast(
          { type: "button", from: client.id, payload },
          client
        );
        client.send({ type: "ack", for: "button", time: Date.now() });
        break;

      case "register":
        // IMPORTANT — délégué à l'expérience actuelle
        this.manager.handle(client, command);
        client.send({ type: "registered", id: client.id });
        break;

      // -----------------------------
      // DEFAULT → redirect to experience
      // -----------------------------
      default:
        // On délègue à l'expérience (SimonGame gère "message": "success")
        this.manager.handle(client, command);
        break;
    }
  }
}