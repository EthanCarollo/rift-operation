import argparse
import json
import asyncio
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import rustymimi
import sentencepiece
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from huggingface_hub import hf_hub_download
from moshi_mlx import models, utils

app = FastAPI()

# Global variables for model and tokenizer - MUST be declared before load_model()
model = None
audio_tokenizer = None
text_tokenizer = None
gen = None
other_codebooks = 0
lm_config = None
MODEL_loaded = False

def load_model():
    global model, audio_tokenizer, text_tokenizer, gen, other_codebooks, lm_config, MODEL_loaded
    if MODEL_loaded:
        return

    print("Loading Kyutai model...")
    hf_repo = "kyutai/stt-1b-en_fr-mlx"
    local_dir = "kyutai-model"
    
    # Download/Load config
    config_path = hf_hub_download(hf_repo, "config.json", local_dir=local_dir)
    with open(config_path, "r") as fobj:
        config_dict = json.load(fobj)
    
    lm_config = models.LmConfig.from_config_dict(config_dict)
    
    # Download/Load weights
    mimi_weights = hf_hub_download(hf_repo, config_dict["mimi_name"], local_dir=local_dir)
    moshi_name = config_dict.get("moshi_name", "model.safetensors")
    moshi_weights = hf_hub_download(hf_repo, moshi_name, local_dir=local_dir)
    tokenizer_path = hf_hub_download(hf_repo, config_dict["tokenizer_name"], local_dir=local_dir)

    # Initialize Model
    model = models.Lm(lm_config)
    model.set_dtype(mx.bfloat16)
    
    # Quantization check
    if moshi_weights.endswith(".q4.safetensors"):
        nn.quantize(model, bits=4, group_size=32)
    elif moshi_weights.endswith(".q8.safetensors"):
        nn.quantize(model, bits=8, group_size=64)

    print(f"Loading weights from {moshi_weights}")
    model.load_weights(moshi_weights, strict=True)

    print(f"Loading tokenizer from {tokenizer_path}")
    text_tokenizer = sentencepiece.SentencePieceProcessor(tokenizer_path)

    print(f"Loading audio tokenizer from {mimi_weights}")
    generated_codebooks = lm_config.generated_codebooks
    other_codebooks = lm_config.other_codebooks
    mimi_codebooks = max(generated_codebooks, other_codebooks)
    audio_tokenizer = rustymimi.Tokenizer(mimi_weights, num_codebooks=mimi_codebooks)

    print("Warming up model...")
    model.warmup()
    
    MODEL_loaded = True
    print("Model loaded.")


# Load model on startup
load_model()

@app.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    # Create a fresh generator for this session
    local_gen = models.LmGen(
        model=model,
        max_steps=4096,
        text_sampler=utils.Sampler(top_k=25, temp=0),
        audio_sampler=utils.Sampler(top_k=250, temp=0.8),
        check=False,
    )
    
    chunk_count = 0
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            chunk_count += 1
            
            # DEBUG: Log received data info
            # print(f"[Chunk {chunk_count}] Received {len(data)} bytes")
            
            # Convert to numpy array
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            
            # DEBUG: Log audio stats
            # print(f"  -> {len(audio_chunk)} float32 samples, min={audio_chunk.min():.4f}, max={audio_chunk.max():.4f}, mean={audio_chunk.mean():.4f}")
            
            # Expected: kyutai_test uses blocksize=1920 samples at 24kHz
            # That's 80ms of audio per block
            # Check if we're getting reasonable chunk sizes
            # expected_samples = 1920  # What kyutai_test uses
            # print(f"  -> Expected ~{expected_samples} samples (80ms at 24kHz), got {len(audio_chunk)}")
            
            # Adapt input to shape (1, 1, N) for encode_step
            audio_chunk = audio_chunk[None, None, :] 
            
            other_audio_tokens = audio_tokenizer.encode_step(audio_chunk)
            other_audio_tokens = mx.array(other_audio_tokens).transpose(0, 2, 1)[:, :, :other_codebooks]
            
            # DEBUG: Log token info
            # print(f"  -> Audio tokens shape: {other_audio_tokens.shape}")
            
            # Process each frame separately if multiple frames returned
            num_frames = other_audio_tokens.shape[1]
            for frame_idx in range(num_frames):
                # Extract single frame: shape (1, 32) -> what model expects
                single_frame = other_audio_tokens[:, frame_idx:frame_idx+1, :]
                
                # Generate
                text_token = local_gen.step(single_frame[0])
                text_token = text_token[0].item()
                
                # DEBUG: Log token
                # if frame_idx == 0:  # Only log first frame to reduce noise
                #     print(f"  -> Text token: {text_token}")
                
                if text_token not in (0, 3):
                    text = text_tokenizer.id_to_piece(text_token)
                    text = text.replace("▁", " ")
                    # print(f"  -> Transcribed: '{text}'")
                    if text:
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
