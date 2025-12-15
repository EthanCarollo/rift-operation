import gc
import uasyncio as asyncio

from src.Framework.Config.ConfigFactory import ConfigFactory
from src.Framework.Button.Button import Button

from src.Core.Controller.StrangerController import StrangerController
from src.Core.Controller.DepthController import DepthController
from src.Core.Controller.LostWokshop.LostController import LostController
from src.Core.Controller.LostWokshop.LostButtonDelegate import LostButtonDelegate

gc.collect()

try:
    config = ConfigFactory.create_cudy_config()
    
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
