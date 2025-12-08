export interface Experience {
  start(): void;          // Called when experience becomes active
  stop(): void;           // Cleanup if needed
  handleCommand(client: any, cmd: any): void;
}