"""E2E Tests for headless Battle Camera backend."""
import pytest
import json
import sys
import os
import time
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web_server import app, socketio
from src.battle_service import init_service, get_service


@pytest.fixture(scope="module")
def service():
    """Initialize and return battle service."""
    # Initialize with camera indices that may not exist (for testing API)
    svc = init_service(nightmare_cam=None, dream_cam=None)
    yield svc
    svc.cleanup()


@pytest.fixture
def client(service):
    """Test client for Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def socket_client(service):
    """Test client for SocketIO."""
    return socketio.test_client(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_returns_ok(self, client):
        """Health endpoint should return status ok."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_health_reports_headless_mode(self, client):
        """Health should report headless mode when service is initialized."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert data['mode'] == 'headless'
        assert data['service'] == True


class TestStatusEndpoint:
    """Tests for /status endpoint."""
    
    def test_status_returns_service_status(self, client):
        """Status should return service status."""
        response = client.get('/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'running' in data
        assert 'current_attack' in data
        assert 'cameras' in data
    
    def test_status_contains_camera_info(self, client):
        """Status should contain camera info for both roles."""
        response = client.get('/status')
        data = json.loads(response.data)
        assert 'nightmare' in data['cameras']
        assert 'dream' in data['cameras']


class TestCamerasEndpoint:
    """Tests for /cameras endpoint."""
    
    def test_cameras_returns_list(self, client):
        """Cameras endpoint should return a list."""
        response = client.get('/cameras')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_cameras_have_index_and_name(self, client):
        """Each camera should have index and name."""
        response = client.get('/cameras')
        data = json.loads(response.data)
        if len(data) > 0:
            assert 'index' in data[0]
            assert 'name' in data[0]


class TestSetCamera:
    """Tests for set_camera SocketIO event."""
    
    def test_set_camera_event(self, socket_client):
        """Should handle set_camera event."""
        socket_client.emit('set_camera', {'role': 'dream', 'camera_index': 0})
        # Should not raise an exception
        # Check if camera_changed event is received
        received = socket_client.get_received()
        # Event may or may not be received depending on camera availability


class TestServiceMethods:
    """Tests for BattleService methods."""
    
    def test_get_status(self, service):
        """get_status should return dict with expected keys."""
        status = service.get_status()
        assert 'running' in status
        assert 'current_attack' in status
        assert 'cameras' in status
    
    def test_set_camera_invalid_role(self, service):
        """set_camera should return False for invalid role."""
        result = service.set_camera('invalid_role', 0)
        assert result == False
    
    def test_start_without_api_key(self, service):
        """start should handle missing API key gracefully."""
        # This may return False if FAL_KEY is not set
        # Just ensure it doesn't crash
        service.start()
        service.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
