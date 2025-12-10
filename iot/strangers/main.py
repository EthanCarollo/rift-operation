import gc
import uasyncio as asyncio
from src.Core.EspController import EspController
from src.Framework.ConfigFactory import ConfigFactory

gc.collect()

try:
    # Use basic ethan house config, easier for what we want lol
    config = ConfigFactory.create_ethan_house_config()
    
    controller = EspController(config)
    asyncio.run(controller.main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
    pass
finally:
    if 'controller' in locals():
        controller.cleanup()