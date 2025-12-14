import ujson
from lib.websocketclient import connect
from config import DEVICE_ID, WORKSHOP, SEND_HELLO_ON_CONNECT
from .utils import log, now_ms


class WsClient:
    # Minimal WebSocket client (auto reconnect, JSON send, non-blocking recv)
    def __init__(self, url: str):
        self.url = url
        self.socket = None

    def ensure_connected(self) -> bool:
        if self.socket:
            return True

        try:
            log("WS connecting:", self.url)
            self.socket = connect(self.url, timeout=8)
            log("WS connected")

            if SEND_HELLO_ON_CONNECT:
                self.send_json({
                    "type": "hello",
                    "value": {"deviceId": DEVICE_ID, "workshop": WORKSHOP}
                })

            return True
        except Exception as e:
            log("WS connect error:", repr(e))
            self.socket = None
            return False

    def send_json(self, obj) -> bool:
        try:
            if not self.ensure_connected():
                return False
            msg = ujson.dumps(obj)
            self.socket.send(msg)
            log("WS >>", msg)
            return True
        except Exception as e:
            log("WS send error:", repr(e))
            self.close(reason="send_error")
            return False

    def poll_recv(self):
        """Return a raw text message if available"""
        if not self.socket:
            return None
        try:
            if self.socket.poll(0):
                return self.socket.recv()
        except Exception as e:
            log("WS recv error:", repr(e))
            self.close(reason="recv_error")
        return None

    def close(self, reason: str = "client_close") -> None:
        if self.socket:
            try:
                msg = {
                    "type": "disconnect",
                    "value": {
                        "deviceId": DEVICE_ID,
                        "workshop": WORKSHOP,
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
        log("WS closed")
