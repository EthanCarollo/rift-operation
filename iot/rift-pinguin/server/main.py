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
    streaming_buffer = "" # 📝 Buffer for reactive QA
    
    try:
        while True:
            # Wait for data (can be audio bytes or text question)
            message = await websocket.receive()
            
            # 🛑 Check for disconnect
            if message["type"] == "websocket.disconnect":
                print(f"Client disconnected (clean) after {chunk_count} chunks")
                break

            if "bytes" in message:
                # 🎙️ Handle Audio (Transcription)
                data = message["bytes"]
                chunk_count += 1
                
                texts = await stt_service.process_audio_chunk(data, local_gen)
                
                current_batch_text = ""
                for text in texts:
                    # Send transcription piece to client
                    await websocket.send_text(f"stt: {text}")
                    
                    # Update session context
                    session_transcription += text
                    current_batch_text += text
                    streaming_buffer += text
                    words_since_last_index += 1
                
                # 🧠 Reactive QA: Detect if the buffer contains a question
                interrogative_keywords = ["?", "qui", "quoi", "où", "quand", "comment", "pourquoi", "quel", "quelle", "est-ce que"]
                lower_buffer = streaming_buffer.lower()
                
                contains_question = any(kw in lower_buffer for kw in interrogative_keywords)
                
                # If we detect a question OR the buffer is getting long
                if (contains_question and len(streaming_buffer) > 10) or len(streaming_buffer) > 200:
                    print(f"🔍 Question détectée (buffer) : {streaming_buffer}")
                    
                    # Try to answer (threshold slightly higher for auto-triggers)
                    qa_result = qa_service.answer(streaming_buffer, min_confidence=0.4)
                    
                    if qa_result['confidence'] > 0.4:
                        print(f"💡 Réponse auto : {qa_result['answer']}")
                        await websocket.send_json({
                            "type": "qa_answer",
                            "answer": qa_result['answer'],
                            "confidence": qa_result['confidence'],
                            "time_ms": qa_result['time_ms']
                        })
                        # Clear buffer after successful answer to avoid repeat triggers
                        streaming_buffer = ""
                    elif len(streaming_buffer) > 200:
                        # Clear buffer if it's too long without a match
                        streaming_buffer = ""

                # The index only contains what was loaded from the DB at startup.
                
            elif "text" in message:
                # ❓ Handle Text (Question for the QA system)
                question = message["text"]
                print(f"Question received: {question}")
                
                # Get answer from QA module (Directly from static index)
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
        print(f"Client disconnected via disconnect exception after {chunk_count} chunks")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        # Only try to close if we didn't just crash on receiving
    finally:
        try:
            await websocket.close()
        except:
            pass


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
