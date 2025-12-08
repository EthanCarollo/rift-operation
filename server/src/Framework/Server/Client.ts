import { WebSocket } from "ws";

export class Client {
  socket: WebSocket;
  id: string;
  role?: string;

  constructor(socket: WebSocket) {
    this.socket = socket;
    this.id = Math.random().toString(36).slice(2);
    this.role = undefined;
  }

  send(data: any) {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }
}
