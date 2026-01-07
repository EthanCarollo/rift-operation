from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from services.KyutaiSttService import KyutaiSttService
from services.PinguinQaService import PinguinQaService

from typing import Dict, Any
import socket
import base64
import asyncio
import websockets
import json
from config import WS_SERVER_URI


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

local_ip = get_local_ip()
print(f"Local network address: http://{local_ip}:8000")

stt_service = KyutaiSttService()
qa_service = PinguinQaService()

# Global State
IS_ACTIVE = False
connected_clients: list[WebSocket] = []

async def broadcast_state(state: str):
    print(f"📡 [BROADCAST] Sending state '{state}' to {len(connected_clients)} clients")
    if not connected_clients:
        return
    
    message = json.dumps({
        "type": "stranger_state",
        "state": state
    })
    
    to_remove = []
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception as e:
            print(f"❌ Failed to broadcast to client: {e}")
            to_remove.append(client)
            
    for client in to_remove:
        if client in connected_clients:
            connected_clients.remove(client)

@asynccontextmanager
async def lifespan(app: FastAPI):
    stt_service.load_model()
    qa_service.load_model()
    # Start the connection to the main server
    asyncio.create_task(connect_to_main_server())
    yield
    # Clean up resources if needed
    pass

app = FastAPI(lifespan=lifespan)

async def connect_to_main_server():
    global IS_ACTIVE
    uri = WS_SERVER_URI
    while True:
        try:
            print(f"🔄 [MAIN SERVER] Attempting to connect to {uri}...")
            async with websockets.connect(uri) as websocket:
                print(f"✅ [MAIN SERVER] Connected to {uri}")
                # Send presence message to websocket panel
                await websocket.send(json.dumps({"device_id": "pinguin-server"}))
                
                while True:
                    try:
                        message_str = await websocket.recv()
                        print(f"📩 [MAIN SERVER] Received: {message_str}")
                        
                        try:
                            message = json.loads(message_str)
                            if isinstance(message, dict):
                                state = message.get("stranger_state")
                                if state == "step_2":
                                    IS_ACTIVE = True
                                    print("🟢 [STATE] Server ACTIVATED remotely")
                                    # Broadcast translated state to Swift clients
                                    await broadcast_state("active")
                                elif state == "step_3":
                                    IS_ACTIVE = False
                                    print("🔴 [STATE] Server DEACTIVATED remotely")
                                    # Broadcast translated state to Swift clients
                                    await broadcast_state("inactive")
                        except json.JSONDecodeError:
                            print(f"⚠️ [MAIN SERVER] Could not parse JSON: {message_str}")
                            
                    except websockets.ConnectionClosed:
                        print("⚠️ [MAIN SERVER] Connection closed")
                        break
        except Exception as e:
            print(f"❌ [MAIN SERVER] Connection failed: {e}")
        
        # Wait before reconnecting
        await asyncio.sleep(5)


# Servir les fichiers audio
import os
os.makedirs("audio", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

async def send_qa_response(websocket: WebSocket, qa_result: Dict[str, Any]):
    """Helper to consistently send QA answers with Base64 audio."""
    audio_base64 = None
    audio_file = qa_result.get('audio_file')
    
    audio_base64 = None
    audio_file = qa_result.get('audio_file')
    confidence = qa_result.get('confidence', 0.0)
    
    # User Rule: Only play audio if confidence >= 65%
    if audio_file and confidence >= 0.65:
        try:
            audio_path = os.path.join("audio", audio_file)
            print(f"📂 [QA] Loading audio: {audio_path}")
            if os.path.exists(audio_path):
                with open(audio_path, "rb") as f:
                    file_content = f.read()
                    audio_base64 = base64.b64encode(file_content).decode('utf-8')
                    print(f"✅ [QA] Audio encoded ({len(audio_base64)} chars)")
            else:
                print(f"❌ [QA] Audio file missing: {audio_path}")
        except Exception as e:
            print(f"❌ [QA] Error encoding audio: {e}")
    
    await websocket.send_json({
        "type": "qa_answer",
        "answer": qa_result['answer'],
        "confidence": qa_result['confidence'],
        "audio_base64": audio_base64,
        "audio_file": audio_file,
        "time_ms": qa_result['time_ms']
    })

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"Client connected (Total: {len(connected_clients)})")
    
    # Send current state immediately on connection
    try:
        current_state = "active" if IS_ACTIVE else "inactive"
        await websocket.send_json({
            "type": "stranger_state",
            "state": current_state
        })
    except Exception as e:
        print(f"Error sending initial state: {e}")
    
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
                if websocket in connected_clients:
                    connected_clients.remove(websocket)
                break
                
            if not IS_ACTIVE:
                # ⏸️ Server is inactive, ignore input but keep connection alive
                # Optional: rate limit this log if it's too spammy
                if chunk_count % 50 == 0:
                    print("😴 [SERVER] Inactive - ignoring input")
                continue

            if "bytes" in message:
                # 🎙️ Handle Audio (Transcription)
                data = message["bytes"]
                chunk_count += 1
                
                if chunk_count % 20 == 0:
                    print(f"🎤 [SERVER] Received chunk #{chunk_count} ({len(data)} bytes)")
                
                # 🛡️ Protection: Reset generator if context is getting full (8192 is hard limit)
                if hasattr(local_gen, 'step_idx') and local_gen.step_idx > 7500:
                    print(f"⚠️ [STT] Resetting generator (step_idx: {local_gen.step_idx}) to avoid context overflow")
                    local_gen = stt_service.create_generator()

                try:
                    texts = await stt_service.process_audio_chunk(data, local_gen)
                except Exception as e:
                    print(f"❌ [STT] Error processing chunk: {e}")
                    await websocket.send_json({
                        "type": "system_error",
                        "message": "STT processing error. Resetting session."
                    })
                    local_gen = stt_service.create_generator()
                    continue
                
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
                # 🧠 Reactive QA: Detect if the buffer contains a question
                # User Request: Only trigger on "?" (ignore keywords like 'quelle')
                contains_question = "?" in streaming_buffer
                
                # If we detect a question OR the buffer is getting long
                if (contains_question and len(streaming_buffer) > 10) or len(streaming_buffer) > 200:
                    # 🎯 Extraction de la dernière phrase uniquement (la question)
                    import re
                    sentences = re.split(r'[.!?]+', streaming_buffer)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    
                    question_to_ask = sentences[-1] if sentences else streaming_buffer
                    
                    print(f"🔍 Question détectée (sentence) : {question_to_ask}")
                    
                    # Try to answer (threshold slightly higher for auto-triggers)
                    qa_result = qa_service.answer(question_to_ask, min_confidence=0.4)
                    
                    if qa_result['confidence'] > 0.4:
                        print(f"💡 Réponse auto : {qa_result['answer']}")
                        
                        # LOGGING: Explicitly mark the start of "talking"
                        print(f"🔊 [SERVER] SENDING ANSWER with audio to client ({len(qa_result.get('audio_file', ''))} chars filename)")
                        
                        await send_qa_response(websocket, qa_result)
                        
                        print(f"🔇 [SERVER] ANSWER SENT")
                        
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
                
                # Send answer back using helper
                await send_qa_response(websocket, qa_result)

    except WebSocketDisconnect:
        print(f"Client disconnected via disconnect exception after {chunk_count} chunks")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        # Only try to close if we didn't just crash on receiving
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
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
