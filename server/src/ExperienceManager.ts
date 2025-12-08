import { Depth } from "./experiences/Depth";
import { Experience } from "./experiences/Experience";
import { Server } from "./Server";

export class ExperienceManager {
  private current: Experience | null = null;
  private server: Server;

  constructor(server: Server) {
    this.server = server;
  }

  start(name: string) {
    if (this.current) this.current.stop();

    switch (name) {
      case "depth":
        this.current = new Depth(this.server);
        break;
      default:
        throw new Error("Unknown experience: " + name);
    }

    this.current.start();
  }

  handle(client: any, cmd: any) {
    if (this.current) this.current.handleCommand(client, cmd);
  }
}