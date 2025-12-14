import time

class Logger:
    LOG_LEVEL_DEBUG = 0
    LOG_LEVEL_INFO = 1
    LOG_LEVEL_WARNING = 2
    LOG_LEVEL_ERROR = 3
    LOG_LEVEL_NONE = 4
    
    def __init__(self, name, level=LOG_LEVEL_INFO, esp32_mode=False, max_log_size=100):
        self.name = name
        self.level = level
        self.esp32_mode = esp32_mode
        self.max_log_size = max_log_size
        self.log_buffer = []
    
    def set_level(self, level):
        self.level = level
    
    def debug(self, message):
        if self.level <= Logger.LOG_LEVEL_DEBUG:
            self._log("DEBUG", message)
    
    def info(self, message):
        if self.level <= Logger.LOG_LEVEL_INFO:
            self._log("INFO", message)
    
    def warning(self, message):
        if self.level <= Logger.LOG_LEVEL_WARNING:
            self._log("WARNING", message)
    
    def error(self, message):
        if self.level <= Logger.LOG_LEVEL_ERROR:
            self._log("ERROR", message)
    
    def _log(self, level, message):
        timestamp = time.time() if self.esp32_mode else time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{self.name}] {message}"
        
        if self.esp32_mode:
            print(log_entry)
        else:
            print(log_entry)
        
        # Maintain log buffer
        self.log_buffer.append(log_entry)
        if len(self.log_buffer) > self.max_log_size:
            self.log_buffer.pop(0)
    
    def get_logs(self):
        return self.log_buffer