import { RiftOperationServer } from "./Core/Server/RiftOperationServer";

const ports = [8000, 8001, 8002];

ports.forEach(port => {
  new RiftOperationServer(port);
});