import gc
import uasyncio as asyncio
from src.Core.EspController2 import EspController2
from src.Framework.Config.ConfigFactory import ConfigFactory

gc.collect()

try:
    config = ConfigFactory.create_alice_house_config()
    
    controller = EspController2(config)
    asyncio.run(controller.main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
    pass
finally:
    if 'controller' in locals():
        controller.cleanup()