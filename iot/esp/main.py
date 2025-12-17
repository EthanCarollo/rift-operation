import gc
import uasyncio as asyncio
from env import controller

gc.collect()

try:
    asyncio.run(controller.main())
except KeyboardInterrupt:
    pass

except Exception as e:
    print(e)

finally:
    if "controller" in locals():
        controller.cleanup()

