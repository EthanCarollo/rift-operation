from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from services.KyutaiSttService import KyutaiSttService

# Initialize Kyutai Service
stt_service = KyutaiSttService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    stt_service.load_model()
    yield
    # Clean up the ML models and release the resources
    pass

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    # Create a fresh generator for this session
    local_gen = stt_service.create_generator()
    
    chunk_count = 0
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            chunk_count += 1
            
            # Process chunk via service
            texts = await stt_service.process_audio_chunk(data, local_gen)
            
            for text in texts:
                await websocket.send_text(text)

    except WebSocketDisconnect:
        print(f"Client disconnected after {chunk_count} chunks")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Get local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    
    print(f"Local network address: http://{local_ip}:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
