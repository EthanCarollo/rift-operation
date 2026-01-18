import threading
import base64
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

from src.Framework.Network.AbstractWebServer import AbstractWebServer
from src.Core.Config import Config
from src.Core.Camera.CameraSettings import get_camera_settings, update_camera_settings, reset_camera_settings
from src.Core.Camera.CameraScanner import CameraScanner

class BattleWebServer(AbstractWebServer):
    """
    Web Server implementation for Battle Camera monitoring.
    Contains Flask app and SocketIO logic.
    """

    def __init__(self, service_provider):
        """
        Args:
            service_provider: Function that returns the active BattleService instance, or None.
        """
        self.app = Flask(__name__)
        CORS(self.app, origins="*")
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*", 
            async_mode='threading', 
            max_http_buffer_size=10*1024*1024
        )
        self.service_provider = service_provider
        
        self._remote_devices_map = {}
        self._assignments = {'dream': None, 'nightmare': None}
        self._debug_mode = False

        self._register_routes()
        self._register_socket_events()

    def _get_service(self):
        return self.service_provider()

    def start(self, host: str = '0.0.0.0', port: int = 5010):
        print(f"[BattleWebServer] Starting on http://{host}:{port}")
        
        # Inject socketio into service if available
        service = self._get_service()
        if service:
            service.set_socketio(self.socketio)
            print("[BattleWebServer] SocketIO injected into Service")

        self.socketio.run(
            self.app, 
            host=host, 
            port=port, 
            debug=False, 
            use_reloader=False, 
            allow_unsafe_werkzeug=True
        )

    def stop(self):
        pass

    def _register_routes(self):
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "ok",
                "mode": "headless",
                "service": self._get_service() is not None
            })

        @self.app.route('/status')
        def status():
            service = self._get_service()
            if service:
                try:
                    return jsonify(service.get_status())
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
            return jsonify({"error": "No service available"}), 500

        @self.app.route('/cameras')
        def get_cameras():
            # Server side cameras
            cams = CameraScanner.list_cameras()
            return jsonify([{"index": idx, "name": name} for idx, name in cams])

        @self.app.route('/camera_settings', methods=['GET'])
        def route_get_settings():
            return jsonify(get_camera_settings())

        @self.app.route('/camera_settings', methods=['POST'])
        def route_update_settings():
            data = request.get_json() or {}
            new_settings = update_camera_settings(data)
            self.socketio.emit('camera_settings_updated', new_settings)
            return jsonify(new_settings)

        @self.app.route('/camera_settings/reset', methods=['POST'])
        def route_reset_settings():
            new_settings = reset_camera_settings()
            self.socketio.emit('camera_settings_updated', new_settings)
            return jsonify(new_settings)
            
        @self.app.route('/debug')
        def debug_cameras():
            service = self._get_service()
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

        # KNN Routes
        @self.app.route('/knn/samples', methods=['GET'])
        def get_knn_samples():
            service = self._get_service()
            if service and service.knn:
                return jsonify(service.knn.get_counts())
            return jsonify({})

        @self.app.route('/knn/add_sample', methods=['POST'])
        def add_knn_sample():
            data = request.json
            label = data.get('label')
            image_b64 = data.get('image')
            if not label or not image_b64:
                return jsonify({'error': 'Missing label or image'}), 400
            
            service = self._get_service()
            if service and service.knn:
                image_bytes = base64.b64decode(image_b64)
                success = service.knn.add_sample(image_bytes, label)
                print(f"[BattleWebServer] KNN: Added sample '{label}' -> {'OK' if success else 'FAIL'}")
                return jsonify({'success': success})
            return jsonify({'error': 'Service not available'}), 500

        @self.app.route('/knn/predict', methods=['POST'])
        def predict_knn():
            data = request.json
            image_b64 = data.get('image')
            if not image_b64:
                return jsonify({'error': 'Missing image'}), 400
            
            service = self._get_service()
            if service and service.knn:
                image_bytes = base64.b64decode(image_b64)
                label, distance = service.knn.predict(image_bytes)
                return jsonify({'label': label, 'distance': distance})
            return jsonify({'error': 'Service not available'}), 500

        @self.app.route('/knn/delete_label', methods=['POST'])
        def delete_knn_label():
            data = request.json
            label = data.get('label')
            if not label:
                return jsonify({'error': 'Missing label'}), 400
            service = self._get_service()
            if service and service.knn:
                service.knn.delete_label(label)
                print(f"[BattleWebServer] KNN: Deleted all samples of '{label}'")
                return jsonify({'success': True})
            return jsonify({'error': 'Service not available'}), 500

        # Remote Devices
        @self.app.route('/remote/devices', methods=['GET'])
        def get_remote_devices():
            all_devices = []
            seen = set()
            for d_list in self._remote_devices_map.values():
                for d in d_list:
                    if d['deviceId'] not in seen:
                        all_devices.append(d)
                        seen.add(d['deviceId'])
            return jsonify(all_devices)

        @self.app.route('/remote/assignments', methods=['GET'])
        def get_assignments():
            return jsonify(self._assignments)

        @self.app.route('/remote/debug_mode', methods=['GET'])
        def get_debug_mode():
            return jsonify({'debug_mode': self._debug_mode})


    def _register_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            print(f"[BattleWebServer] Client connected: {request.sid}")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"[BattleWebServer] Client disconnected: {request.sid}")
            sid = request.sid
            if sid in self._remote_devices_map:
                del self._remote_devices_map[sid]

        @self.socketio.on('process_frame')
        def handle_process_frame(data):
            role = data.get('role')
            image_b64 = data.get('image')
            if not role or not image_b64: return

            # Broadcast raw camera frame to all clients
            self.socketio.emit('camera_preview', {'role': role, 'frame': image_b64})

            service = self._get_service()
            if service:
                try:
                    image_bytes = base64.b64decode(image_b64)
                    service.process_client_frame(role, image_bytes)
                except Exception as e:
                    print(f"[BattleWebServer] Frame processing failed: {e}")

        @self.socketio.on('update_camera_settings')
        def handle_update_camera_settings(data):
            new_settings = update_camera_settings(data)
            self.socketio.emit('camera_settings_updated', new_settings)

        @self.socketio.on('register_client')
        def handle_register_client(data):
            devices = data.get('devices', [])
            sid = request.sid
            print(f"[BattleWebServer] Client {sid} registered {len(devices)} devices")
            self._remote_devices_map[sid] = devices
            
            # Update admins
            all_devices = []
            for d_list in self._remote_devices_map.values():
                all_devices.extend(d_list)
            self.socketio.emit('remote_devices_update', all_devices)
            
            # Send assignments
            for role, device_id in self._assignments.items():
                if device_id:
                    self.socketio.emit('set_device', {'role': role, 'deviceId': device_id}, room=sid)

        @self.socketio.on('assign_device')
        def handle_assign_device(data):
            role = data.get('role')
            device_id = data.get('deviceId')
            if role and device_id:
                print(f"[BattleWebServer] Assigning {device_id} to {role}")
                self._assignments[role] = device_id
                self.socketio.emit('set_device', {'role': role, 'deviceId': device_id})

        @self.socketio.on('set_debug_mode')
        def handle_set_debug_mode(data):
            self._debug_mode = data.get('enabled', False)
            print(f"[BattleWebServer] Debug mode: {self._debug_mode}")
            self.socketio.emit('debug_mode_changed', {'enabled': self._debug_mode})
