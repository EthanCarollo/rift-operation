import pytest
import base64
import time
from unittest.mock import MagicMock, patch

from src.Core import init_service, get_service
from src.Core.Network.BattleWebServer import BattleWebServer
from src.Core.Config import Config

# Mock Image bytes
MOCK_IMAGE_BYTES = b"fake_image_data"
MOCK_IMAGE_B64 = base64.b64encode(MOCK_IMAGE_BYTES).decode('utf-8')

@pytest.fixture
def mock_dependencies():
    """Mock out heavy/external dependencies."""
    with patch('src.Core.Utils.KNNRecognizer') as MockKNN, \
         patch('src.Core.Utils.FalFluxEditor') as MockEditor, \
         patch('src.Core.Utils.VisionBackgroundRemover') as MockBG, \
         patch('src.Core.RiftWebSocket') as MockRift:
        
        # Configure KNN to recognize "key"
        knn_instance = MockKNN.return_value
        knn_instance.predict.return_value = ("key", 0.5)
        
        # Configure Editor to return success
        editor_instance = MockEditor.return_value
        editor_instance.edit_image.return_value = (b"generated_image", 1.0)
        
        # Configure BG Remover
        bg_instance = MockBG.return_value
        bg_instance.remove_background.return_value = (b"final_image", 1.0)
        
        yield {
            'knn': knn_instance,
            'editor': editor_instance,
            'rift': MockRift.return_value
        }

@pytest.fixture
def app_server(mock_dependencies):
    """Initialize Service and WebServer."""
    # Ensure Config enables KNN
    Config.ENABLE_KNN = True
    
    # Init Service
    service = init_service()
    
    # Init Server
    server = BattleWebServer(service_provider=get_service)
    
    # Start service (mock thread monitoring to avoid dangling threads if possible, 
    # but service.start() spawns a daemon thread which is fine for tests)
    service.start()
    
    yield server
    
    service.cleanup()

def test_workflow_image_roundtrip(app_server, mock_dependencies):
    """
    Test the full flow:
    1. Client connects via WebSocket.
    2. Client sends 'process_frame'.
    3. Server processes (Mock KNN -> Mock AI -> Mock BG).
    4. Client receives 'output_frame'.
    """
    flask_app = app_server.app
    socketio = app_server.socketio
    
    # Create Test Client
    client = socketio.test_client(flask_app)
    assert client.is_connected()
    
    # Set current attack to "PORTE" (DOOR) so "key" is a valid counter
    # This ensures is_valid_counter=True in logic
    service = get_service()
    service.current_attack = Config.Attack.DOOR 
    
    # Send Frame
    client.emit('process_frame', {
        'role': 'nightmare',
        'image': MOCK_IMAGE_B64
    })
    
    # Wait for events (processing happens in thread)
    # socketio.test_client usually captures emitted events immediately if they happen sync,
    # but our service uses threading. We might need to sleep slightly or rely on callback structure.
    # However, flask_socketio.test_client.get_received() is useful.
    
    # Allow thread to switch
    time.sleep(0.5)
    
    received = client.get_received()
    
    # Filter events
    preview_events = [e for e in received if e['name'] == 'camera_preview']
    output_events = [e for e in received if e['name'] == 'output_frame']
    
    # 1. Verify Camera Preview (Broadcast immediately)
    assert len(preview_events) > 0
    assert preview_events[0]['args'][0]['role'] == 'nightmare'
    
    # 2. Verify Output Frame (Processed via mocks)
    # If this fails, it might be due to threading. 
    # The logging in BattleService should help debug.
    assert len(output_events) > 0, "No output_frame received - processing failed?"
    
    data = output_events[0]['args'][0]
    assert data['role'] == 'nightmare'
    assert data['frame'] is not None
    
    # Verify KNN was called
    mock_dependencies['knn'].predict.assert_called()
    
    # Verify Editor was called
    mock_dependencies['editor'].edit_image.assert_called()

    client.disconnect()
