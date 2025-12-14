import gc
import uasyncio as asyncio
from src.Core.EspController import EspController
from src.Framework.ConfigFactory import ConfigFactory

# Collect garbage before starting
gc.collect()

try:
    # Create depth configuration
    config = ConfigFactory.create_depth_config()
    
    # Override role if needed (uncomment and set to "parent" for parent device)
    # config.depth.role = "parent"
    
    # Create and run controller
    controller = EspController(config)
    asyncio.run(controller.main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"Error: {e}")
    pass
finally:
    if 'controller' in locals():
        controller.cleanup()