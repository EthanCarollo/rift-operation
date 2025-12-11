import * as http from "http";
import * as fs from "fs";
import * as path from "path";
import Logger from "../Utils/Logger";

export interface HttpRequestHandlerOptions {
  staticDir: string;
}

export class HttpRequestHandler {
  private staticDir: string;

  constructor(options: HttpRequestHandlerOptions) {
    this.staticDir = options.staticDir;
  }

  public setCorsHeaders(res: http.ServerResponse): void {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  }

  public handleOptions(req: http.IncomingMessage, res: http.ServerResponse): boolean {
    if (req.method === 'OPTIONS') {
      this.setCorsHeaders(res);
      res.writeHead(200);
      res.end();
      return true;
    }
    return false;
  }

  public serveStaticFile(url: string, res: http.ServerResponse): void {
    const filePath = path.join(this.staticDir, url);
    const resolvedPath = path.resolve(filePath);
    const staticPath = path.resolve(this.staticDir);

    if (!resolvedPath.startsWith(staticPath)) {
      this.sendForbidden(res);
      return;
    }

    fs.readFile(filePath, (err, data) => {
      if (err) {
        if (err.code === 'ENOENT') {
          this.sendNotFound(res);
        } else {
          Logger.error(`Error reading static file: ${err.message}`);
          this.sendInternalError(res);
        }
        return;
      }

      const ext = path.extname(filePath).toLowerCase();
      const contentType = this.getContentType(ext);
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    });
  }

  public serveHtmlFile(fileName: string, res: http.ServerResponse): void {
    const filePath = path.join(this.staticDir, fileName);
    fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) {
        Logger.error(`Error reading HTML file: ${err.message}`);
        this.sendInternalError(res);
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
  }

  public serveJson(data: any, res: http.ServerResponse): void {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
  }



  private getContentType(ext: string): string {
    const contentTypes: { [key: string]: string } = {
      '.html': 'text/html',
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.gif': 'image/gif',
      '.svg': 'image/svg+xml',
      '.ico': 'image/x-icon'
    };
    return contentTypes[ext] || 'text/plain';
  }

  public sendNotFound(res: http.ServerResponse): void {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }

  public sendForbidden(res: http.ServerResponse): void {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
  }

  public sendInternalError(res: http.ServerResponse): void {
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('Internal Server Error');
  }
}
