import gc
import uasyncio as asyncio

from src.Framework.Config.ConfigFactory import ConfigFactory
from src.Core.Lost.LostConfig import LostConfigFactory
from src.Core.Depth.DepthConfig import DepthConfigFactory

from src.Core.Controller.Stranger.StrangerParentController import StrangerParentController
from src.Core.Controller.TableController import TableController
from src.Core.Controller.DepthController import DepthController
from src.Core.Controller.LostController import LostController 

gc.collect()

try:
    config = ConfigFactory.create_cudy_stranger_config()
    # config = LostConfigFactory.create_child()
    # config = LostConfigFactory.create_parent()
    # config = DepthConfigFactory.create_default_child()

    # controller = TableController(config)
    controller = StrangerParentController(config)
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

