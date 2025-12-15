import * as http from "http";
import * as path from "path";
import { RawData } from "ws";
import { Client } from "../../Framework/Server/Client";
import { BaseWebSocketServer } from "../../Framework/Server/Server";
import { HttpRequestHandler } from "../../Framework/Server/HttpRequestHandler";
import Logger from "../../Framework/Utils/Logger";

export class RiftOperationServer extends BaseWebSocketServer {
  private httpServer: http.Server;
  private httpHandler: HttpRequestHandler;

  constructor(port: number) {
    const httpServer = http.createServer();
    
    super({
      server: httpServer,
      path: "/ws"
    });

    this.httpServer = httpServer;
    const staticDir = path.join(__dirname, '../../../public');
    
    this.httpHandler = new HttpRequestHandler({
      staticDir
    });

    this.httpServer.on('request', (req, res) => {
      if (this.httpHandler.handleOptions(req, res)) {
        return;
      }
      this.httpHandler.setCorsHeaders(res);
      this.handleRequest(req, res);
    });

    this.httpServer.listen(port, () => {
      Logger.log(`Server running on port ${port} (HTTP + WebSocket on /ws)`);
    });
  }

  private handleRequest(req: http.IncomingMessage, res: http.ServerResponse): void {
    const url = req.url || '/';

    if (url === '/' || url === '/clients') {
      this.httpHandler.serveHtmlFile('clients.html', res);
    } else if (url === '/api/clients') {
      this.serveClientsApi(res);
    } else {
      this.httpHandler.serveStaticFile(url, res);
    }
  }

  private serveClientsApi(res: http.ServerResponse): void {
    try {
      const clients = this.getClientsData();
      this.httpHandler.serveJson({ clients, total: clients.length }, res);
    } catch (error) {
      Logger.error(`Error serving clients API: ${error}`);
      this.httpHandler.serveJson({ error: 'Internal Server Error' }, res);
    }
  }

  onConnection(client: Client): void {
    Logger.log("New WebSocket client connection");
  }

  onMessage(client: Client, msg: RawData): void {
    try {
      const parsed = JSON.parse(msg.toString());
      
      // Capture device_id identity
      if (parsed.device_id) {
        client.deviceId = parsed.device_id;
      }
      
      this.broadcast(parsed, client);
    } catch {
      Logger.error("Didn't receive JSON on WebSocket message.");
    }
  }

  onClose(client: Client): void {
  }

  public close(): void {
    this.httpServer.close();
  }
}
