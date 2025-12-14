import time
from config import DEBUG


def log(*args):
    if DEBUG:
        print("[IOT]", *args)


def now_ms():
    return time.ticks_ms()
