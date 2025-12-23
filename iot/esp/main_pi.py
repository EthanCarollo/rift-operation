
import asyncio
import sys

# Standard Python Entry Point for RIFT on Raspberry Pi

from src.Framework.Config.ConfigFactory import ConfigFactory
from src.Core.Controller.RiftController import RiftController

async def main():
    # Setup Config using standard factory
    # Ensure ConfigFactory doesn't import embedded libs (verified earlier)
    config = ConfigFactory.create_rift_config()
    
    # Create Unified Controller
    # It will auto-detect "PI" platform and load RiftHardwarePi
    controller = RiftController(config)
    
    # Run
    await controller.main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
