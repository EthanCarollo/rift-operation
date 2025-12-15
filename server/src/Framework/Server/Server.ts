import { WebSocketServer, WebSocket, RawData } from "ws";
import * as http from "http";
import { Client } from "./Client";
import Logger from "../Utils/Logger";

export interface BaseWebSocketServerOptions {
  server?: http.Server;
  port?: number;
  path?: string;
}

export abstract class BaseWebSocketServer {
  protected wss: WebSocketServer;
  protected clients: Set<Client>;
  protected path: string;

  constructor(options: BaseWebSocketServerOptions) {
    this.clients = new Set();
    this.path = options.path || "/";

    if (options.server) {
      this.wss = new WebSocketServer({
        server: options.server,
        path: this.path
      });
      Logger.log(`WebSocket server attached to HTTP server at path: ${this.path}`);
    } else if (options.port) {
      this.wss = new WebSocketServer({
        port: options.port,
        path: this.path
      });
      Logger.log(`Standalone WebSocket server running on port ${options.port} at path: ${this.path}`);
    } else {
      throw new Error("Either 'server' or 'port' must be specified");
    }

    this.setupWebSocketHandlers();
  }

  private setupWebSocketHandlers(): void {
    this.wss.on("connection", (socket: WebSocket) => {
      const client = new Client(socket);
      this.clients.add(client);
      this.onConnection(client);

      socket.on("message", (msg) => {
        this.onMessage(client, msg);
      });

      socket.on("close", () => {
        this.onClose(client);
        this.clients.delete(client);
      });
    });
  }

  abstract onConnection(client: Client): void;
  abstract onMessage(client: Client, msg: RawData): void;
  abstract onClose(client: Client): void;

  public broadcast(message: any, exclude?: Client): void {
    for (const client of this.clients) {
      if (client !== exclude) client.send(message);
    }
  }

  public getClients(): Set<Client> {
    return this.clients;
  }

  public getClientsData(): { id: string; role: string; readyState: number; readyStateText: string; }[] {
    return Array.from(this.clients).map(client => ({
      id: client.id,
      deviceId: client.deviceId || 'unknown',
      role: client.role || 'unknown',
      readyState: client.socket.readyState,
      readyStateText: this.getReadyStateText(client.socket.readyState)
    }));
  }

  private getReadyStateText(state: number): string {
    switch (state) {
      case 0: return 'CONNECTING';
      case 1: return 'OPEN';
      case 2: return 'CLOSING';
      case 3: return 'CLOSED';
      default: return 'UNKNOWN';
    }
  }
}
