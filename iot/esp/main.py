import gc
import uasyncio as asyncio
from src.Core.Controller.StrangerController import StrangerController
from src.Core.DepthController import DepthController
from src.Framework.Config.ConfigFactory import ConfigFactory

gc.collect()

try:
    config = ConfigFactory.create_cudy_config()
    controller = StrangerController(config)
    controller = DepthController(config)
    asyncio.run(controller.main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
    pass
finally:
    if 'controller' in locals():
        controller.cleanup()