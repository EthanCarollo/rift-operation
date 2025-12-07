import { RiftOperationServer } from "./Core/Server/RiftOperationServer";
import Logger from "./Core/Utils/Logger"

const port = 8080;
new RiftOperationServer(port);
Logger.log(`Server is running on port ${port}`);