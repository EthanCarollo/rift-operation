import { WebSocketServer, WebSocket, RawData } from "ws";
import { Client } from "../../Framework/Server/Client";

export abstract class Server {
    wss: WebSocketServer;
    clients: Set<Client>;
    
    constructor(port: number) {
        this.wss = new WebSocketServer({ port });
        this.clients = new Set();
        
        this.wss.on("connection", (socket: WebSocket) => {
            const client = new Client(socket);
            this.clients.add(client);
            
            this.onConnection(client)

            socket.on("message", (msg) => { this.onMessage(client, msg)} );
            
            socket.on("close", () => {
                this.onClose(client)
                this.clients.delete(client);
            });
        });
    }
    
    abstract onConnection(client: Client): void;

    abstract onMessage(client: Client, msg: RawData): void;

    abstract onClose(client: Client): void;
    
    broadcast(message: any, exclude?: Client) {
        for (const client of this.clients) {
            if (client !== exclude) client.send(message);
        }
    }
}
