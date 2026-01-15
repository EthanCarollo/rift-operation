"""Web server for Battle Camera monitoring (Headless mode only)."""
import threading
import time
import base64
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")
# Increasing max_http_buffer_size for large base64 images
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', max_http_buffer_size=10*1024*1024)

_running = False


@socketio.on('connect')
def handle_connect():
    print(f"[WebServer] Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[WebServer] Client disconnected: {request.sid}")


def _get_service():
    """Get BattleService instance."""
    try:
        from src.battle_service import get_service
        return get_service()
    except:
        return None


@app.route('/health')
def health():
    """Health check endpoint."""
    service = _get_service()
    return jsonify({
        "status": "ok",
        "mode": "headless",
        "service": service is not None
    })


@app.route('/status')
def status():
    """Get current battle status."""
    service = _get_service()
    
    if service:
        try:
            return jsonify(service.get_status())
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No service available"}), 500


@app.route('/cameras')
def get_cameras():
    """Get list of available cameras (server side - unused in client mode but kept for debugging)."""
    # In client-mode this returns server cams, not client cams.
    from src import list_cameras
    cams = list_cameras()
    return jsonify([{"index": idx, "name": name} for idx, name in cams])


@app.route('/debug')
def debug_cameras():
    """Debug endpoint to check service status."""
    service = _get_service()
    
    if not service:
        return jsonify({"error": "No service"}), 500
    
    debug_info = {}
    try:
        for role, state in service.roles.items():
            debug_info[role] = {
                "processing": state.processing,
                "recognition_status": state.recognition_status,
                "last_gen": state.last_gen_time,
                "has_last_output": state.last_output is not None
            }
    except Exception as e:
        debug_info["error"] = str(e)
    
    return jsonify(debug_info)


@socketio.on('process_frame')
def handle_process_frame(data):
    """Handle incoming camera frame from frontend for AI processing."""
    role = data.get('role')
    image_b64 = data.get('image')
    
    if not role or not image_b64:
        return

    # Broadcast raw camera frame to all clients (for config preview)
    socketio.emit('camera_preview', {'role': role, 'frame': image_b64})

    service = _get_service()
    if service:
        try:
            # Decode base64
            image_bytes = base64.b64decode(image_b64)
            
            # Delegate processing to service
            service.process_client_frame(role, image_bytes)
        except Exception as e:
            print(f"[WebServer] Frame processing failed: {e}")


@socketio.on('set_camera')
def handle_set_camera(data):
    # Legacy - maintained for compatibility but unused
    pass


@app.route('/camera_settings', methods=['GET'])
def get_camera_settings():
    """Get current camera compression settings."""
    from src.camera import get_camera_settings as get_settings
    return jsonify(get_settings())


@app.route('/camera_settings', methods=['POST'])
def update_camera_settings():
    """Update camera compression settings."""
    from src.camera import update_camera_settings as update_settings
    
    data = request.get_json() or {}
    new_settings = update_settings(data)
    
    # Broadcast to all connected clients
    socketio.emit('camera_settings_updated', new_settings)
    
    return jsonify(new_settings)


@app.route('/camera_settings/reset', methods=['POST'])
def reset_camera_settings():
    """Reset camera settings to defaults."""
    from src.camera import reset_camera_settings as reset_settings
    
    new_settings = reset_settings()
    socketio.emit('camera_settings_updated', new_settings)
    
    return jsonify(new_settings)


@socketio.on('update_camera_settings')
def handle_update_camera_settings(data):
    """Handle real-time camera settings update via SocketIO."""
    from src.camera import update_camera_settings as update_settings
    
    new_settings = update_settings(data)
    socketio.emit('camera_settings_updated', new_settings)


# --- REMOTE CAMERA CONFIGURATION ---

# Store remote devices sent by Battle Client
# { 'client_sid': [ {deviceId, label}, ... ] }
_remote_devices_map = {} 
# Assignments: { 'dream': deviceId, 'nightmare': deviceId }
_assignments = { 'dream': None, 'nightmare': None }

@socketio.on('register_client')
def handle_register_client(data):
    """Battle Client registers its available devices."""
    global _remote_devices_map
    devices = data.get('devices', [])
    sid = request.sid
    
    print(f"[WebServer] Client {sid} registered {len(devices)} devices")
    _remote_devices_map[sid] = devices
    
    # Broadcast updated list to admin clients
    all_devices = []
    for d_list in _remote_devices_map.values():
        all_devices.extend(d_list)
        
    socketio.emit('remote_devices_update', all_devices)
    
    # Send current assignments back to this client immediately
    for role, device_id in _assignments.items():
        if device_id:
            socketio.emit('set_device', {'role': role, 'deviceId': device_id}, room=sid)


@socketio.on('disconnect')
def handle_disconnect():
    global _remote_devices_map
    sid = request.sid
    if sid in _remote_devices_map:
        print(f"[WebServer] Client {sid} disconnected")
        del _remote_devices_map[sid]
        # Notify admins? maybe unnecessary spam


@app.route('/remote/devices', methods=['GET'])
def get_remote_devices():
    """Get all connected remote devices."""
    all_devices = []
    # Deduplicate by deviceId if needed, or keep all
    seen = set()
    for d_list in _remote_devices_map.values():
        for d in d_list:
            if d['deviceId'] not in seen:
                all_devices.append(d)
                seen.add(d['deviceId'])
    return jsonify(all_devices)

@app.route('/remote/assignments', methods=['GET'])
def get_assignments():
    return jsonify(_assignments)


@socketio.on('assign_device')
def handle_assign_device(data):
    """Admin assigns a device to a role."""
    role = data.get('role')
    device_id = data.get('deviceId')
    
    if role and device_id:
        print(f"[WebServer] Assigning {device_id} to {role}")
        _assignments[role] = device_id
        
        # Broadcast assignment to ALL clients (Battle Client will pick it up)
        socketio.emit('set_device', {'role': role, 'deviceId': device_id})


# --- DEBUG MODE ---
_debug_mode = False

@app.route('/remote/debug_mode', methods=['GET'])
def get_debug_mode():
    return jsonify({'debug_mode': _debug_mode})

@socketio.on('set_debug_mode')
def handle_set_debug_mode(data):
    """Admin toggles debug mode."""
    global _debug_mode
    _debug_mode = data.get('enabled', False)
    print(f"[WebServer] Debug mode: {_debug_mode}")
    
    # Broadcast to ALL clients
    socketio.emit('debug_mode_changed', {'enabled': _debug_mode})


def start_server_headless(host='0.0.0.0', port=5010):
    """Start the web server in blocking mode."""
    service = _get_service()
    if service:
        # Inject socketio into service for emitting events
        service.set_socketio(socketio)
        print("[WebServer] SocketIO injected into Service")
    
    print(f"[WebServer] Starting on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)


def stop_server():
    """Stop server helpers."""
    pass
