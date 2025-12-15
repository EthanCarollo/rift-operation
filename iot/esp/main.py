import gc
import uasyncio as asyncio
from src.Core.Controller.StrangerController import StrangerController
from src.Framework.Config.ConfigFactory import ConfigFactory

gc.collect()

try:
    config = ConfigFactory.create_cudy_config()
    controller = StrangerController(config)
    asyncio.run(controller.main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
    pass
finally:
    if 'controller' in locals():
        controller.cleanup()