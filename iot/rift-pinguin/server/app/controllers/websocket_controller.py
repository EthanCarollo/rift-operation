from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import numpy as np
from app.services.kyutai_service import kyutai_service

router = APIRouter()

@router.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    # Create session generator
    try:
        generator = kyutai_service.create_generator()
    except RuntimeError:
        print("Model not loaded yet")
        await websocket.close(reason="Server initializing")
        return

    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Convert to numpy array
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            
            # Process with service
            text_token = kyutai_service.process_audio_chunk(generator, audio_chunk)
            
            # Decode and send
            text = kyutai_service.decode_token(text_token)
            if text:
                await websocket.send_text(text)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in websocket session: {e}")
        try:
            await websocket.close()
        except:
            pass
