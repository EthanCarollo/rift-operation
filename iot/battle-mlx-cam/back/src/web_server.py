"""Web server for Battle Camera monitoring (Headless mode only)."""
import threading
import time
import base64
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

_running = False


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
        return jsonify(service.get_status())
    else:
        return jsonify({"error": "No service available"}), 500


@app.route('/cameras')
def get_cameras():
    """Get list of available cameras."""
    from src import list_cameras
    cams = list_cameras()
    return jsonify([{"index": idx, "name": name} for idx, name in cams])


@socketio.on('set_camera')
def handle_set_camera(data):
    """Handle camera selection from config page."""
    role = data.get('role')
    cam_index = data.get('camera_index')
    
    if role is None or cam_index is None:
        return
    
    service = _get_service()
    
    if service:
        success = service.set_camera(role, cam_index)
        if success:
            socketio.emit('camera_changed', {'role': role, 'camera_index': cam_index})


@app.route('/camera_settings', methods=['GET'])
def get_camera_settings():
    """Get current camera compression settings."""
    from src.camera import get_camera_settings as get_settings
    return jsonify(get_settings())


@app.route('/camera_settings', methods=['POST'])
def update_camera_settings():
    """Update camera compression settings."""
    from src.camera import update_camera_settings as update_settings
    from flask import request
    
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


def _broadcast_loop():
    """Background thread to broadcast camera frames and status."""
    global _running
    _running = True
    
    while _running:
        service = _get_service()
        
        if service:
            try:
                socketio.emit('status', service.get_status())
                
                for role, panel in service.panels.items():
                    if panel.camera and panel.last_frame:
                        b64 = base64.b64encode(panel.last_frame).decode('utf-8')
                        socketio.emit('camera_frame', {
                            'role': role,
                            'frame': b64,
                            'recognition': panel.recognition_status
                        })
                    
                    if panel.last_output:
                        b64 = base64.b64encode(panel.last_output).decode('utf-8')
                        socketio.emit('output_frame', {
                            'role': role,
                            'frame': b64
                        })
            except Exception as e:
                print(f"[WebServer] Broadcast error: {e}")
        
        time.sleep(0.1)  # 10 FPS


def start_server_headless(host='0.0.0.0', port=5010):
    """Start the web server in blocking mode."""
    broadcast_thread = threading.Thread(target=_broadcast_loop, daemon=True)
    broadcast_thread.start()
    
    print(f"[WebServer] Starting on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)


def stop_server():
    """Stop the broadcast loop."""
    global _running
    _running = False
