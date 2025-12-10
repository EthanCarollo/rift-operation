# boot.py
# Runs at boot before main.py

import gc
import network

try:
    network.WLAN(network.AP_IF).active(False)
except:
    pass

gc.collect()
