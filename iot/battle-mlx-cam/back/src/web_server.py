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

# Global reference to battle view (set from main.py)
_battle_view = None
_running = False

def set_battle_view(view):
    """Set reference to BattleView for accessing cameras and state."""
    global _battle_view
    _battle_view = view

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "battle_view": _battle_view is not None
    })

@app.route('/status')
def status():
    """Get current battle status."""
    if not _battle_view:
        return jsonify({"error": "No battle view"}), 500
    
    return jsonify({
        "running": _battle_view.running,
        "current_attack": _battle_view.current_attack,
        "ws_connected": _battle_view.ws.socket is not None if _battle_view.ws else False,
        "ws_last_state": _battle_view.ws.last_state if _battle_view.ws else None
    })

@app.route('/cameras')
def get_cameras():
    """Get list of available cameras."""
    from src import list_cameras
    cams = list_cameras()
    return jsonify([{"index": idx, "name": name} for idx, name in cams])

@socketio.on('set_camera')
def handle_set_camera(data):
    """Handle camera selection from config page."""
    if not _battle_view:
        return
    
    role = data.get('role')
    cam_index = data.get('camera_index')
    
    if role in _battle_view.panels and cam_index is not None:
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
        if _battle_view:
            try:
                # Broadcast status
                status_data = {
                    "running": _battle_view.running,
                    "current_attack": _battle_view.current_attack,
                    "ws_state": _battle_view.ws.last_state if _battle_view.ws else None
                }
                socketio.emit('status', status_data)
                
                # Broadcast camera frames
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
                        
                        # Also send output if available
                        if hasattr(panel.output, '_last_image') and panel.output._last_image:
                            socketio.emit('output_frame', {
                                'role': role,
                                'frame': panel.output._last_image
                            })
                            
            except Exception as e:
                print(f"[WebServer] Broadcast error: {e}")
        
        time.sleep(0.1)  # 10 FPS

def start_server(host='0.0.0.0', port=5000):
    """Start the web server in a background thread."""
    def run():
        # Start broadcast loop
        broadcast_thread = threading.Thread(target=_broadcast_loop, daemon=True)
        broadcast_thread.start()
        
        print(f"[WebServer] Starting on http://{host}:{port}")
        socketio.run(app, host=host, port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
    
    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()
    return server_thread

def stop_server():
    """Stop the broadcast loop."""
    global _running
    _running = False
