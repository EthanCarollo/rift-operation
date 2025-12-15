import gc
import asyncio as asyncio
from src.Core.Controller.StrangerController import StrangerController
from iot.esp.src.Core.Controller.DepthController import DepthController
from iot.esp.src.Core.Controller.LostController import LostController
from src.Framework.Config.ConfigFactory import ConfigFactory

gc.collect()

try:
    config = ConfigFactory.create_cudy_config()
    controller = StrangerController(config)
    controller = DepthController(config)
    controller = LostController(config)
    asyncio.run(controller.main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
    pass
finally:
    if 'controller' in locals():
        controller.cleanup()