import asyncio
import sys

# Standard Python Entry Point for RIFT on Raspberry Pi
from src.Framework.Config.ConfigFactory import ConfigFactory
from src.Core.Controller.RiftController import RiftController

async def main():
    config = ConfigFactory.create_rift_config()
    controller = RiftController(config)
    # Run
    await controller.main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
