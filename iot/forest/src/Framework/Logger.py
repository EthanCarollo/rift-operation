import time

class Logger:
    LEVEL_DEBUG = 0
    LEVEL_INFO = 1
    LEVEL_ERROR = 2

    def __init__(self, name="IOT", level=LEVEL_INFO):
        self.name = name
        self.level = level

    def _ts(self):
        try:
            t = time.localtime()
            return "%02d:%02d:%02d" % (t[3], t[4], t[5])
        except:
            return "--:--:--"

    def _log(self, level_name, level_value, *args):
        if level_value < self.level:
            return
        print("[%s][%s][%s]" % (self.name, level_name, self._ts()), *args)

    def debug(self, *args):
        self._log("DEBUG", self.LEVEL_DEBUG, *args)

    def info(self, *args):
        self._log("INFO", self.LEVEL_INFO, *args)

    def error(self, *args):
        # errors always printed
        self._log("ERROR", self.LEVEL_ERROR, *args)
