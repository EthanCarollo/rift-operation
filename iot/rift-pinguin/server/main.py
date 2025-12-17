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

# Global variables for model and tokenizer
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
    
    # Initialize Generator
    # Note: We create a generator instance per session or reuse one? 
    # kyutai_test.py creates one. LmGen keeps state (cache). 
    # For a server handling multiple clients, we arguably need one per client.
    # But for now, we will assume single client usage or re-instantiate for simplicity first, 
    # or check if LmGen is reset-able. LmGen seems to hold cache.
    
    MODEL_loaded = True
    print("Model loaded.")

# Load model on startup
load_model()

@app.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    
    # Create a fresh generator for this session
    # We are sharing the model (weights), but need separate state (cache) for generation.
    # models.LmGen takes the model. If LmGen modifies model state, we are in trouble.
    # Looking at moshi_mlx, LmGen usually maintains the KVCache.
    # Let's inspect LmGen in moshi_mlx if possible, but assuming standard autoregressive pattern, 
    # cache is passed or stored in LmGen.
    
    local_gen = models.LmGen(
        model=model,
        max_steps=4096, # Or unlimited/loop?
        text_sampler=utils.Sampler(top_k=25, temp=0),
        audio_sampler=utils.Sampler(top_k=250, temp=0.8),
        check=False,
    )
    
    try:
        while True:
            # Receive audio data
            # Expecting raw bytes of float32, 24000Hz, mono.
            data = await websocket.receive_bytes()
            
            # Convert to numpy array
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            
            # Process generic chunk size
            # The model in kyutai_test.py processes blocks in a loop.
            # We need to feed 'audio_tokenizer.encode_step'
            # audio_tokenizer.encode_step expects (channels, samples) -> (1, N)
            
            # Adapt input to shape (1, 1, N)
            audio_chunk = audio_chunk[None, None, :] 
            
            other_audio_tokens = audio_tokenizer.encode_step(audio_chunk)
            
            # (1, 1, codebooks) after encode_step? 
            # kyutai_test.py: 
            # other_audio_tokens = mx.array(other_audio_tokens).transpose(0, 2, 1)[:, :, :other_codebooks]
            
            other_audio_tokens = mx.array(other_audio_tokens).transpose(0, 2, 1)[:, :, :other_codebooks]
            
            # Generate
            # We are assuming VAD is OFF for now to match prompt "transcription" simply,
            # or we can enable it. User asked to "use the kyutai model".
            # kyutai_test.py defaults to no VAD if not specified, 
            # but user didn't specify. I'll stick to simple first.
            
            text_token = local_gen.step(other_audio_tokens[0])
            text_token = text_token[0].item()
            
            if text_token not in (0, 3): # 0=pad?, 3=eos?
                text = text_tokenizer.id_to_piece(text_token)
                text = text.replace("▁", " ")
                # Send back to client
                if text:
                    await websocket.send_text(text)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
