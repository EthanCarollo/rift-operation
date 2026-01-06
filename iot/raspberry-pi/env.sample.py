import gc
import uasyncio as asyncio

from src.Framework.Config.ConfigFactory import ConfigFactory

from src.Core.Controller.Stranger.StrangerNightmareController import StrangerNightmareController

"""
En gros ici tu instanties ton controller dans controller quoi, sans commit
c'est comme un .env, donc faut le rename env.py
Et il est .gitignore, donc si tu le commit, tu es reconnu coupable.
""" 

gc.collect()

config = ConfigFactory.create_cudy_stranger_config()
controller = StrangerNightmareController(config)

