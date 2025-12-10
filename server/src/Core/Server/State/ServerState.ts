import { Client } from "../../../Framework/Server/Client";
import { RiftOperationServer } from "../RiftOperationServer";

export default abstract class ServerState {
    public constructor(protected server: RiftOperationServer){ }

    public abstract onConnection(client: Client): void;
    public abstract onMessage(client: Client, message: JSON): void;
    public abstract onClose(client: Client): void;
}