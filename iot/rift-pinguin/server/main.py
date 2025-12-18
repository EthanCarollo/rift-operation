from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from services.KyutaiSttService import KyutaiSttService
from services.PinguinQaService import PinguinQaService

stt_service = KyutaiSttService()
qa_service = PinguinQaService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    stt_service.load_model()
    qa_service.load_model()
    yield
    # Clean up resources if needed
    pass

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    # Create a fresh generator for this session
    local_gen = stt_service.create_generator()
    
    # Transcription state for this session
    session_transcription = ""
    chunk_count = 0
    words_since_last_index = 0
    
    try:
        while True:
            # Wait for data (can be audio bytes or text question)
            message = await websocket.receive()
            
            if "bytes" in message:
                # 🎙️ Handle Audio (Transcription)
                data = message["bytes"]
                chunk_count += 1
                
                texts = await stt_service.process_audio_chunk(data, local_gen)
                
                for text in texts:
                    # Send transcription piece to client
                    await websocket.send_text(f"stt: {text}")
                    
                    # Update session context
                    session_transcription += text
                    words_since_last_index += 1
                
                # Periodically update the QA index (every 5 new word-pieces)
                if words_since_last_index >= 5:
                    qa_service.index_transcription(session_transcription)
                    words_since_last_index = 0
                    
            elif "text" in message:
                # ❓ Handle Text (Question for the QA system)
                question = message["text"]
                print(f"Question received: {question}")
                
                # Make sure we've indexed the latest words
                if words_since_last_index > 0:
                    qa_service.index_transcription(session_transcription)
                    words_since_last_index = 0
                
                # Get answer from QA module
                qa_result = qa_service.answer(question)
                print(f"Answer generated: {qa_result['answer']} (confidence: {qa_result['confidence']:.2f})")
                
                # Send answer back
                await websocket.send_json({
                    "type": "qa_answer",
                    "answer": qa_result['answer'],
                    "confidence": qa_result['confidence'],
                    "time_ms": qa_result['time_ms']
                })

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
