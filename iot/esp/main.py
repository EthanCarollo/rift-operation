import gc
import uasyncio as asyncio

from src.Framework.Config.ConfigFactory import ConfigFactory

from src.Core.Controller.StrangerController import StrangerController
from src.Core.Controller.DepthController import DepthController
from src.Core.Controller.LostController import LostController 

gc.collect()

try:
    config = ConfigFactory.create_cudy_config()

    controller = StrangerController(config)
    # controller = DepthController(config)
    # controller = LostController(config)

    asyncio.run(controller.main())

except KeyboardInterrupt:
    pass

except Exception as e:
    print(e)

finally:
    if "controller" in locals():
        controller.cleanup()
