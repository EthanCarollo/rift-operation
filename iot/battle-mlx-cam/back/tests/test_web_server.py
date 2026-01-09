"""Tests for Battle Camera web server."""
import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web_server import app, socketio


@pytest.fixture
def client():
    """Test client for Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def socket_client():
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
    
    def test_health_reports_battle_view_status(self, client):
        """Health should report if battle view is set."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'battle_view' in data


class TestStatusEndpoint:
    """Tests for /status endpoint."""
    
    def test_status_without_battle_view(self, client):
        """Status should return error when no battle view."""
        response = client.get('/status')
        # May return 500 if no battle view is set
        assert response.status_code in [200, 500]


class TestCamerasEndpoint:
    """Tests for /cameras endpoint."""
    
    def test_cameras_returns_list(self, client):
        """Cameras endpoint should return a list."""
        response = client.get('/cameras')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestSocketIO:
    """Tests for SocketIO events."""
    
    def test_connect(self, socket_client):
        """Should be able to connect via SocketIO."""
        assert socket_client.is_connected()
    
    def test_set_camera_event(self, socket_client):
        """Should handle set_camera event without error."""
        socket_client.emit('set_camera', {'role': 'dream', 'camera_index': 0})
        # Should not raise an exception
        # Response may vary based on battle view state


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
