import time
import ujson
from lib.websocketclient import connect

def now_ms():
    return time.ticks_ms()


class WebSocketClient:
    # Minimal WebSocket client (auto reconnect, JSON send, non-blocking recv)
    def __init__(self, ws_config, device_config, send_hello_on_connect, logger):
        self.url = ws_config.url
        self.device = device_config
        self.send_hello_on_connect = send_hello_on_connect
        self.log = logger
        self.socket = None

    def ensure_connected(self):
        if self.socket:
            return True

        try:
            self.log.info("WS connecting:", self.url)
            self.socket = connect(self.url, timeout=8)
            self.log.info("WS connected")

            if self.send_hello_on_connect:
                self.send_json({
                    "type": "hello",
                    "value": {
                        "deviceId": self.device.device_id,
                        "workshop": self.device.workshop,
                        "role": self.device.role,
                    }
                })

            return True
        except Exception as e:
            self.log.error("WS connect error:", repr(e))
            self.socket = None
            return False

    def send_json(self, obj):
        try:
            if not self.ensure_connected():
                return False
            msg = ujson.dumps(obj)
            self.socket.send(msg)
            self.log.debug("WS >>", msg)
            return True
        except Exception as e:
            self.log.error("WS send error:", repr(e))
            self.close(reason="send_error")
            return False

    def poll_recv(self):
        """Return raw text message if available, else None"""
        if not self.socket:
            return None
        try:
            if hasattr(self.socket, "poll"):
                if not self.socket.poll(0):
                    return None
            return self.socket.recv()
        except Exception as e:
            self.log.error("WS recv error:", repr(e))
            self.close(reason="recv_error")
            return None

    def close(self, reason="client_close"):
        if self.socket:
            try:
                msg = {
                    "type": "disconnect",
                    "value": {
                        "deviceId": self.device.device_id,
                        "workshop": self.device.workshop,
                        "reason": reason,
                        "tsMs": now_ms(),
                    }
                }
                self.socket.send(ujson.dumps(msg))
            except Exception:
                pass

            try:
                self.socket.close()
            except Exception:
                pass

        self.socket = None
        self.log.info("WS closed")
