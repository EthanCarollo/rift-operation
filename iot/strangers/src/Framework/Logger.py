import utime
import uio
import sys

class Logger:
    LOG_LEVEL_DEBUG = 0
    LOG_LEVEL_INFO = 1
    LOG_LEVEL_WARNING = 2
    LOG_LEVEL_ERROR = 3
    LOG_LEVEL_CRITICAL = 4

    def __init__(self, name="APP", level=LOG_LEVEL_INFO, log_to_file=False, log_file="log.txt", 
                 esp32_mode=True, max_log_size=500):
        self.name = name
        self.level = level
        self.log_to_file = log_to_file
        self.log_file = log_file
        self.esp32_mode = esp32_mode
        self.max_log_size = max_log_size
        self.log_buffer = []
        
        if log_to_file:
            try:
                with open(log_file, 'w') as f:
                    f.write("=== LOG START ===\n")
            except:
                self.log_to_file = False

    def _get_timestamp(self):
        """Get current timestamp in HH:MM:SS format"""
        try:
            year, month, day, hour, minute, second, weekday, yearday = utime.localtime()
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        except:
            return "00:00:00"

    def _get_caller_info(self):
        """Get caller file and line number"""
        if self.esp32_mode:
            # Skip caller info on ESP32 to save memory
            return ""
        
        try:
            # Get the frame of the caller
            frame = sys._getframe(2)
            return f"{frame.f_code.co_filename}:{frame.f_lineno}"
        except:
            return "unknown:0"

    def _format_message(self, level, message):
        """Format log message with timestamp, level, caller info, and message"""
        level_names = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        level_name = level_names[level] if level < len(level_names) else "UNKNOWN"
        
        timestamp = self._get_timestamp()
        
        if self.esp32_mode:
            # Compact format for ESP32 - omit caller info to save memory
            return f"[{timestamp}] [{level_name}] {message}"
        else:
            # Full format for local debugging
            caller_info = self._get_caller_info()
            return f"[{timestamp}] [{level_name}] [{caller_info}] {message}"

    def _log(self, level, message):
        """Internal log method"""
        if level < self.level:
            return
            
        formatted_message = self._format_message(level, message)
        
        # Print to console
        print(formatted_message)
        
        # Write to file if enabled
        if self.log_to_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(formatted_message + '\n')
                    # Rotate log file if it gets too large for ESP32
                    f.flush()
                    import os
                    try:
                        stat = os.stat(self.log_file)
                        if stat[6] > self.max_log_size:  # File size
                            self._rotate_log_file()
                    except:
                        pass
            except:
                pass

    def _rotate_log_file(self):
        """Rotate log file to prevent it from growing too large"""
        try:
            import os
            # Rename current log file
            backup_name = self.log_file + ".bak"
            try:
                os.remove(backup_name)  # Remove old backup
            except:
                pass
            os.rename(self.log_file, backup_name)
            
            # Create new log file
            with open(self.log_file, 'w') as f:
                f.write("=== LOG START ===\n")
        except:
            pass

    def debug(self, message):
        self._log(self.LOG_LEVEL_DEBUG, message)

    def info(self, message):
        self._log(self.LOG_LEVEL_INFO, message)

    def warning(self, message):
        self._log(self.LOG_LEVEL_WARNING, message)

    def error(self, message):
        self._log(self.LOG_LEVEL_ERROR, message)

    def critical(self, message):
        self._log(self.LOG_LEVEL_CRITICAL, message)

    def set_level(self, level):
        """Set the logging level"""
        self.level = level

    def enable_file_logging(self, filename="log.txt"):
        """Enable logging to file"""
        self.log_file = filename
        self.log_to_file = True
        try:
            with open(filename, 'w') as f:
                f.write("=== LOG START ===\n")
        except:
            self.log_to_file = False

    def disable_file_logging(self):
        """Disable logging to file"""
        self.log_to_file = False