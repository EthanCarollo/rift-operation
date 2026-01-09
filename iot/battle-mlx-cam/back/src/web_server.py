"""Web server for Battle Camera monitoring."""
import threading
import time
import base64
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global references
_battle_view = None  # For legacy tkinter mode
_running = False


def set_battle_view(view):
    """Set reference to BattleView for accessing cameras and state (legacy mode)."""
    global _battle_view
    _battle_view = view


def _get_service():
    """Get BattleService instance (headless mode)."""
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
        "mode": "headless" if service else "legacy",
        "service": service is not None,
        "battle_view": _battle_view is not None
    })


@app.route('/status')
def status():
    """Get current battle status."""
    service = _get_service()
    
    if service:
        return jsonify(service.get_status())
    elif _battle_view:
        return jsonify({
            "running": _battle_view.running,
            "current_attack": _battle_view.current_attack,
            "ws_connected": _battle_view.ws.socket is not None if _battle_view.ws else False,
            "ws_last_state": _battle_view.ws.last_state if _battle_view.ws else None
        })
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
        # Headless mode
        success = service.set_camera(role, cam_index)
        if success:
            socketio.emit('camera_changed', {'role': role, 'camera_index': cam_index})
    elif _battle_view and role in _battle_view.panels:
        # Legacy mode
        panel = _battle_view.panels[role]
        try:
            from src import Camera
            if panel.camera:
                panel.camera.close()
            panel.camera = Camera(cam_index)
            panel.camera.open()
            print(f"[WebServer] Set {role} camera to {cam_index}")
            socketio.emit('camera_changed', {'role': role, 'camera_index': cam_index})
        except Exception as e:
            print(f"[WebServer] Failed to set camera: {e}")


def _broadcast_loop():
    """Background thread to broadcast camera frames and status."""
    global _running
    _running = True
    
    while _running:
        service = _get_service()
        
        if service:
            # Headless mode
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
                
        elif _battle_view:
            # Legacy mode
            try:
                status_data = {
                    "running": _battle_view.running,
                    "current_attack": _battle_view.current_attack,
                    "ws_state": _battle_view.ws.last_state if _battle_view.ws else None
                }
                socketio.emit('status', status_data)
                
                for role, panel in _battle_view.panels.items():
                    if panel.camera:
                        frame = panel.camera.capture()
                        if frame:
                            b64 = base64.b64encode(frame).decode('utf-8')
                            socketio.emit('camera_frame', {
                                'role': role,
                                'frame': b64,
                                'recognition': panel.rec_label.cget("text") if hasattr(panel.rec_label, 'cget') else ""
                            })
                        
                        if hasattr(panel.output, '_last_image') and panel.output._last_image:
                            socketio.emit('output_frame', {
                                'role': role,
                                'frame': panel.output._last_image
                            })
            except Exception as e:
                print(f"[WebServer] Broadcast error: {e}")
        
        time.sleep(0.1)  # 10 FPS


def start_server(host='0.0.0.0', port=5010):
    """Start the web server in a background thread (for legacy tkinter mode)."""
    def run():
        broadcast_thread = threading.Thread(target=_broadcast_loop, daemon=True)
        broadcast_thread.start()
        
        print(f"[WebServer] Starting on http://{host}:{port}")
        socketio.run(app, host=host, port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()
    return server_thread


def start_server_headless(host='0.0.0.0', port=5010):
    """Start the web server in blocking mode (for headless mode)."""
    broadcast_thread = threading.Thread(target=_broadcast_loop, daemon=True)
    broadcast_thread.start()
    
    print(f"[WebServer] Starting on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)


def stop_server():
    """Stop the broadcast loop."""
    global _running
    _running = False
