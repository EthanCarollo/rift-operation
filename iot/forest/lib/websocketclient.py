import usocket as socket
import ubinascii as binascii
import urandom
import ure
import ustruct
import uselect

# RFC6455 opcodes
_OP_TEXT = 0x1
_OP_CLOSE = 0x8
_OP_PING = 0x9
_OP_PONG = 0xA

_URL_RE = ure.compile(r"^(ws)://([^/:]+)(?::([0-9]+))?(/.*)?$")


def _parse_ws_url(url):
    m = _URL_RE.match(url)
    if not m:
        raise ValueError("Invalid WS URL (expected ws://host:port/path)")
    host = m.group(2)
    port = m.group(3)
    path = m.group(4)
    port = int(port) if port is not None else 80
    path = path if path else "/"
    return host, port, path


def _read_exact(sock, n):
    """Read exactly n bytes or raise"""
    buf = b""
    while len(buf) < n:
        chunk = sock.read(n - len(buf))
        if not chunk:
            raise OSError("socket closed")
        buf += chunk
    return buf


class WebSocket:
    """Minimal WS client: send text, receive text, non-blocking poll"""
    def __init__(self, sock):
        self._sock = sock
        self._poll = uselect.poll()
        self._poll.register(sock, uselect.POLLIN)

    def poll(self, timeout_ms=0):
        """Return True if incoming data is available"""
        return bool(self._poll.poll(timeout_ms))

    def send(self, msg):
        """Send a masked text frame (required for WS clients)"""
        if isinstance(msg, str):
            payload = msg.encode("utf-8")
        else:
            payload = msg

        length = len(payload)
        first_byte = 0x80 | _OP_TEXT  # FIN + TEXT
        mask_bit = 0x80

        if length < 126:
            header = ustruct.pack("!BB", first_byte, mask_bit | length)
        elif length < (1 << 16):
            header = ustruct.pack("!BBH", first_byte, mask_bit | 126, length)
        else:
            header = ustruct.pack("!BBQ", first_byte, mask_bit | 127, length)

        mask = ustruct.pack("!I", urandom.getrandbits(32))
        masked = bytes(b ^ mask[i & 3] for i, b in enumerate(payload))

        self._sock.write(header)
        self._sock.write(mask)
        self._sock.write(masked)

    def recv(self):
        """Receive one text message (blocking)"""
        b1b2 = self._sock.read(2)
        if not b1b2:
            return None

        b1, b2 = ustruct.unpack("!BB", b1b2)
        fin = (b1 & 0x80) != 0
        opcode = b1 & 0x0F

        masked = (b2 & 0x80) != 0
        length = b2 & 0x7F

        if length == 126:
            length = ustruct.unpack("!H", _read_exact(self._sock, 2))[0]
        elif length == 127:
            length = ustruct.unpack("!Q", _read_exact(self._sock, 8))[0]

        mask_key = b""
        if masked:
            mask_key = _read_exact(self._sock, 4)

        data = _read_exact(self._sock, length)

        if masked:
            data = bytes(b ^ mask_key[i & 3] for i, b in enumerate(data))

        if opcode == _OP_PING:
            # Reply pong
            self._send_control(_OP_PONG, data)
            return None
        if opcode == _OP_CLOSE:
            return None
        if opcode != _OP_TEXT:
            return None
        if not fin:
            # No fragmentation support in this minimal client
            return None

        return data.decode("utf-8")

    def _send_control(self, opcode, payload=b""):
        """Send a masked control frame"""
        length = len(payload)
        first_byte = 0x80 | opcode
        mask_bit = 0x80

        if length < 126:
            header = ustruct.pack("!BB", first_byte, mask_bit | length)
        else:
            header = ustruct.pack("!BBH", first_byte, mask_bit | 126, length)

        mask = ustruct.pack("!I", urandom.getrandbits(32))
        masked = bytes(b ^ mask[i & 3] for i, b in enumerate(payload))

        self._sock.write(header)
        self._sock.write(mask)
        self._sock.write(masked)

    def close(self):
        try:
            self._sock.close()
        except Exception:
            pass


def connect(url, timeout=8):
    """Connect to ws:// and return a WebSocket instance"""
    host, port, path = _parse_ws_url(url)

    sock = socket.socket()
    sock.settimeout(timeout)
    addr = socket.getaddrinfo(host, port)[0][-1]
    sock.connect(addr)

    key = binascii.b2a_base64(bytes(urandom.getrandbits(8) for _ in range(16)))[:-1]

    def send_line(line_bytes):
        sock.write(line_bytes + b"\r\n")

    send_line(b"GET " + path.encode() + b" HTTP/1.1")
    send_line(b"Host: " + host.encode() + b":" + str(port).encode())
    send_line(b"Connection: Upgrade")
    send_line(b"Upgrade: websocket")
    send_line(b"Sec-WebSocket-Key: " + key)
    send_line(b"Sec-WebSocket-Version: 13")
    send_line(b"Origin: http://" + host.encode() + b":" + str(port).encode())
    send_line(b"")

    status = sock.readline()
    if not status:
        sock.close()
        raise OSError("No HTTP response from server")
    if b" 101 " not in status:
        sock.close()
        raise OSError("WebSocket handshake failed: " + status)

    while True:
        h = sock.readline()
        if not h or h == b"\r\n":
            break

    return WebSocket(sock)
