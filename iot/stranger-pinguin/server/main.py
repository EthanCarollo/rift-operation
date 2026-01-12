from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from services.KyutaiSttService import KyutaiSttService, ContextOverflowError
from services.PinguinQaService import PinguinQaService

from typing import Dict, Any
import socket
import base64
import asyncio
import websockets
import json
import argparse
import multiprocessing
from config import (
    WS_SERVER_URI,
    COSMO_PORT, DARK_COSMO_PORT,
    COSMO_AUDIO_MAP, DARK_COSMO_AUDIO_MAP,
    COSMO_DEVICE_ID, DARK_COSMO_DEVICE_ID,
    COSMO_ACTIVATE_STEP, COSMO_DEACTIVATE_STEP,
    DARK_COSMO_ACTIVATE_STEP, DARK_COSMO_DEACTIVATE_STEP,
    DARK_COSMO_DETECTED_AUDIO
)

# Parse CLI arguments
parser = argparse.ArgumentParser(description='Pinguin Server')
parser.add_argument('--mode', choices=['cosmo', 'dark_cosmo', 'both'], default='both',
                    help='Server mode: cosmo (port 8000), dark_cosmo (port 8001), or both (default)')
args = parser.parse_args()

# Configure based on mode (for single server mode)
SERVER_MODE = args.mode
if SERVER_MODE != 'both':
    SERVER_PORT = COSMO_PORT if SERVER_MODE == 'cosmo' else DARK_COSMO_PORT
    AUDIO_MAP_PATH = COSMO_AUDIO_MAP if SERVER_MODE == 'cosmo' else DARK_COSMO_AUDIO_MAP
    DEVICE_ID = COSMO_DEVICE_ID if SERVER_MODE == 'cosmo' else DARK_COSMO_DEVICE_ID
    ACTIVATE_STEP = COSMO_ACTIVATE_STEP if SERVER_MODE == 'cosmo' else DARK_COSMO_ACTIVATE_STEP
    DEACTIVATE_STEP = COSMO_DEACTIVATE_STEP if SERVER_MODE == 'cosmo' else DARK_COSMO_DEACTIVATE_STEP
    print(f"🚀 Starting server in {SERVER_MODE.upper()} mode on port {SERVER_PORT}")
    print(f"📂 Using audio map: {AUDIO_MAP_PATH}")
    print(f"🟢 Activates on: {ACTIVATE_STEP}, Deactivates on: {DEACTIVATE_STEP}")
else:
    # Will be set per-process when running both
    SERVER_PORT = None
    AUDIO_MAP_PATH = COSMO_AUDIO_MAP
    DEVICE_ID = COSMO_DEVICE_ID
    ACTIVATE_STEP = COSMO_ACTIVATE_STEP
    DEACTIVATE_STEP = COSMO_DEACTIVATE_STEP


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
qa_service = PinguinQaService(audio_map_path=AUDIO_MAP_PATH)

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

async def broadcast_dark_cosmo_audio():
    """Broadcasts audio to Swift clients when dark cosmo is detected (Cosmo mode only)."""
    print(f"🌙 [DARK COSMO] Broadcasting audio to {len(connected_clients)} clients")
    if not connected_clients:
        return
    
    # Load audio config from JSON
    audio_file = None
    try:
        with open(DARK_COSMO_DETECTED_AUDIO, 'r') as f:
            config = json.load(f)
            audio_file = config.get('audio_file')
    except Exception as e:
        print(f"❌ [DARK COSMO] Failed to load audio config: {e}")
        return
    
    if not audio_file:
        print("❌ [DARK COSMO] No audio_file specified in config")
        return
    
    # Load and encode the audio file
    audio_base64 = None
    try:
        audio_path = os.path.join("audio", audio_file)
        print(f"📂 [DARK COSMO] Loading audio: {audio_path}")
        if os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                file_content = f.read()
                audio_base64 = base64.b64encode(file_content).decode('utf-8')
                print(f"✅ [DARK COSMO] Audio encoded ({len(audio_base64)} chars)")
        else:
            print(f"❌ [DARK COSMO] Audio file missing: {audio_path}")
            return
    except Exception as e:
        print(f"❌ [DARK COSMO] Error encoding audio: {e}")
        return
    
    # Broadcast to all clients
    message = json.dumps({
        "type": "dark_cosmo_detected",
        "audio_base64": audio_base64,
        "audio_file": audio_file
    })
    
    to_remove = []
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception as e:
            print(f"❌ [DARK COSMO] Failed to broadcast to client: {e}")
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
                # Send presence message to websocket panel with mode-specific device ID
                await websocket.send(json.dumps({"device_id": DEVICE_ID}))
                
                while True:
                    try:
                        message_str = await websocket.recv()
                        print(f"📩 [MAIN SERVER] Received: {message_str}")
                        
                        try:
                            message = json.loads(message_str)
                            if isinstance(message, dict):
                                state = message.get("stranger_state")
                                if state == ACTIVATE_STEP:
                                    IS_ACTIVE = True
                                    print(f"🟢 [STATE] Server ACTIVATED on {ACTIVATE_STEP}")
                                    # Broadcast translated state to Swift clients
                                    await broadcast_state("active")
                                elif state == DEACTIVATE_STEP:
                                    IS_ACTIVE = False
                                    print(f"🔴 [STATE] Server DEACTIVATED on {DEACTIVATE_STEP}")
                                    # Broadcast translated state to Swift clients
                                    await broadcast_state("inactive")
                                
                                # Handle is_dark_cosmo_here (only for Cosmo, not Dark Cosmo)
                                is_dark_cosmo_here = message.get("is_dark_cosmo_here")
                                if is_dark_cosmo_here == True and SERVER_MODE == 'cosmo':
                                    print(f"🌙 [DARK COSMO] Detected! Broadcasting audio to Cosmo clients...")
                                    await broadcast_dark_cosmo_audio()
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
                except ContextOverflowError as e:
                    print(f"🔄 [STT] Context reset: {e}. Creating fresh generator...")
                    local_gen = stt_service.create_generator()
                    
                    # Reprocess any pending chunks that were buffered during reset
                    pending = stt_service.get_pending_chunks()
                    if pending:
                        print(f"🔄 [STT] Reprocessing {len(pending)} buffered audio chunks...")
                        for pending_chunk in pending:
                            try:
                                pending_texts = await stt_service.process_audio_chunk(pending_chunk, local_gen)
                                for text in pending_texts:
                                    await websocket.send_text(f"stt: {text}")
                                    session_transcription += text
                                    streaming_buffer += text
                            except Exception as pe:
                                print(f"⚠️ [STT] Failed to reprocess pending chunk: {pe}")
                    continue
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
                
                # 🧠 Reactive QA: Detect trigger based on server mode
                # Cosmo: triggers on "?" (question)
                # Dark Cosmo: triggers on "." (end of sentence/affirmation)
                if SERVER_MODE == 'dark_cosmo':
                    # Dark Cosmo: detect end of sentence (affirmation)
                    contains_trigger = "." in streaming_buffer
                    trigger_type = "affirmation"
                    min_length = 30  # Require longer phrases for Dark Cosmo
                    min_confidence = 0.6  # Higher confidence threshold
                else:
                    # Cosmo: detect question mark
                    contains_trigger = "?" in streaming_buffer
                    trigger_type = "question"
                    min_length = 10
                    min_confidence = 0.4
                
                # If we detect a trigger OR the buffer is getting long
                if (contains_trigger and len(streaming_buffer) > min_length) or len(streaming_buffer) > 200:
                    # 🎯 Extraction de la dernière phrase
                    import re
                    sentences = re.split(r'[.!?]+', streaming_buffer)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    
                    phrase_to_match = sentences[-1] if sentences else streaming_buffer
                    
                    # Skip if phrase is too short for Dark Cosmo
                    if SERVER_MODE == 'dark_cosmo' and len(phrase_to_match) < 15:
                        continue
                    
                    # Dark Cosmo: require the word "chaussettes" to be present
                    if SERVER_MODE == 'dark_cosmo' and "chaussette" not in phrase_to_match.lower():
                        continue
                    
                    print(f"🔍 {trigger_type.capitalize()} détectée : {phrase_to_match}")
                    
                    # Try to answer with mode-specific confidence threshold
                    qa_result = qa_service.answer(phrase_to_match, min_confidence=min_confidence)
                    
                    if qa_result['confidence'] > min_confidence:
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


def run_server(mode: str):
    """Run a single server in specified mode."""
    import uvicorn
    import subprocess
    import sys
    
    # Launch as subprocess with specific mode
    subprocess.run([sys.executable, __file__, '--mode', mode])


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
    
    if SERVER_MODE == 'both':
        print(f"")
        print(f"🚀 Starting DUAL SERVER mode")
        print(f"   ☀️  Cosmo:      http://{local_ip}:{COSMO_PORT}")
        print(f"   🌙 Dark Cosmo: http://{local_ip}:{DARK_COSMO_PORT}")
        print(f"")
        
        # Start both servers in separate processes
        cosmo_process = multiprocessing.Process(
            target=run_server,
            args=('cosmo',),
            name='CosmoServer'
        )
        dark_cosmo_process = multiprocessing.Process(
            target=run_server,
            args=('dark_cosmo',),
            name='DarkCosmoServer'
        )
        
        try:
            cosmo_process.start()
            dark_cosmo_process.start()
            
            # Wait for both processes
            cosmo_process.join()
            dark_cosmo_process.join()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down both servers...")
            cosmo_process.terminate()
            dark_cosmo_process.terminate()
            cosmo_process.join()
            dark_cosmo_process.join()
            print("✅ Both servers stopped.")
    else:
        # Single server mode
        print(f"Local network address: http://{local_ip}:{SERVER_PORT}")
        uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
