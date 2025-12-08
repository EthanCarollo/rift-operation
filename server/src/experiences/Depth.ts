import { Client } from "../Client";
import { Server } from "../Server";
import { Experience } from "./Experience";

/**
 * Depth Game (ex-Simon)
 * Child reproduces a button sequence
 * Parent reproduces it after
 * After 3 partitions → unlock
 */

export class Depth implements Experience {
  private server: Server;
  private child?: Client;
  private parent?: Client;
  private AUTO_PARENT = true;

  private index = 0;
  private state: "WAIT_CHILD" | "WAIT_PARENT" | "FINISHED" = "WAIT_CHILD";

  // 👇 tes partitions ici (modifie si besoin)
  private PARTITIONS = ["1,2,1,3", "3,3,1", "2,1,2,3"];

  constructor(server: Server) {
    this.server = server;
  }

  start() {
    console.log("DEPTH EXPERIENCE STARTED");
    this.index = 0;
    this.state = "WAIT_CHILD";
  }

  stop() {
    console.log("DEPTH EXPERIENCE STOPPED");
  }

  handleCommand(client: Client, cmd: any) {
    const payload = cmd.payload ?? cmd.value;

    switch (cmd.type) {
      case "register":
        this.register(client, payload);
        break;

      case "message":
        if (payload === "success") this.onSuccess(client);
        break;
    }
  }

    private register(client: Client, role: "child" | "parent") {
        client.role = role;

        if (role === "child") this.child = client;
        if (role === "parent") this.parent = client;

        console.log(`DEPTH: ${role} registered → ${client.id}`);

        // --- AUTO-PARENT MODE ---
        if (this.AUTO_PARENT && role === "child" && !this.parent) {
            console.log("AUTO-PARENT MODE: Virtual parent created");
            this.parent = client; // we don't use it, just to bypass logic
        }

        // --- START GAME AS SOON AS CHILD IS PRESENT ---
        if (this.child && this.parent && this.index === 0) {
            console.log("DEPTH: starting first turn");
            this.startChildTurn();
        }
    }

  private startChildTurn() {
    this.state = "WAIT_CHILD";
    console.log("→ DEPTH turn CHILD", this.index);
    this.child?.send({
      type: "partition",
      value: this.PARTITIONS[this.index],
    });
  }

  private startParentTurn() {
    this.state = "WAIT_PARENT";
    console.log("→ DEPTH turn PARENT", this.index);
    this.parent?.send({
      type: "partition",
      value: this.PARTITIONS[this.index],
    });
  }

  private onSuccess(client: Client) {
    console.log(`SUCCESS from ${client.role}`);

    if (client.role === "child" && this.state === "WAIT_CHILD") {
      if (this.AUTO_PARENT) {
        console.log("AUTO-PARENT MODE: Simulating parent success");
        this.index++;
        if (this.index >= this.PARTITIONS.length) this.finish();
        else this.startChildTurn();
      } else {
        this.startParentTurn();
      }
    } else if (client.role === "parent" && this.state === "WAIT_PARENT") {
      this.index++;
      if (this.index >= this.PARTITIONS.length) this.finish();
      else this.startChildTurn();
    }
  }

  private finish() {
    console.log("DEPTH COMPLETED → UNLOCK");
    this.server.broadcast({ type: "unlock", value: true });
    this.state = "FINISHED";
  }
}