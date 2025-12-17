# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "moshi_mlx==0.2.12",
#     "numpy",
#     "rustymimi",
#     "sentencepiece",
#     "sounddevice",
# ]
# ///

import argparse
import json
import queue
import os
import sys

import mlx.core as mx
import mlx.nn as nn
import rustymimi
import sentencepiece
import sounddevice as sd
from moshi_mlx import models, utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-steps", default=4096, type=int)
    parser.add_argument("--model-dir", default="rift-pinguin/Moshi/kyutai-model", help="Path to the local model directory")
    args = parser.parse_args()

    model_dir = args.model_dir
    if not os.path.exists(model_dir):
        print(f"Error: Model directory '{model_dir}' not found.")
        sys.exit(1)

    print(f"Using local model directory: {model_dir}")

    # Load config
    config_path = os.path.join(model_dir, "config.json")
    if not os.path.exists(config_path):
        print(f"Error: config.json not found in {model_dir}")
        sys.exit(1)
        
    with open(config_path, "r") as fobj:
        lm_config_dict = json.load(fobj)

    # Resolve paths from config or defaults
    mimi_filename = lm_config_dict.get("mimi_name", "mimi-pytorch-e351c8d8@125.safetensors")
    moshi_filename = lm_config_dict.get("moshi_name", "model.safetensors")
    tokenizer_filename = lm_config_dict.get("tokenizer_name", "tokenizer_en_fr_audio_8000.model")

    mimi_weights = os.path.join(model_dir, mimi_filename)
    moshi_weights = os.path.join(model_dir, moshi_filename)
    tokenizer_path = os.path.join(model_dir, tokenizer_filename)

    # Verify files exist
    for path, name in [(mimi_weights, "Mimi weights"), (moshi_weights, "Moshi weights"), (tokenizer_path, "Tokenizer")]:
        if not os.path.exists(path):
            print(f"Error: {name} not found at {path}")
            sys.exit(1)

    # Initialize model
    lm_config = models.LmConfig.from_config_dict(lm_config_dict)
    model = models.Lm(lm_config)
    model.set_dtype(mx.bfloat16)

    # Quantization check based on filename suffix (mirrors original script logic)
    if moshi_weights.endswith(".q4.safetensors"):
        nn.quantize(model, bits=4, group_size=32)
    elif moshi_weights.endswith(".q8.safetensors"):
        nn.quantize(model, bits=8, group_size=64)

    print(f"Loading model weights from {moshi_weights}")
    model.load_weights(moshi_weights, strict=True)

    print(f"Loading text tokenizer from {tokenizer_path}")
    text_tokenizer = sentencepiece.SentencePieceProcessor(tokenizer_path)  # type: ignore

    print(f"Loading audio tokenizer from {mimi_weights}")
    generated_codebooks = lm_config.generated_codebooks
    other_codebooks = lm_config.other_codebooks
    mimi_codebooks = max(generated_codebooks, other_codebooks)
    audio_tokenizer = rustymimi.Tokenizer(mimi_weights, num_codebooks=mimi_codebooks)  # type: ignore

    print("Warming up the model")
    model.warmup()
    
    # Initialize generator
    gen = models.LmGen(
        model=model,
        max_steps=args.max_steps,
        text_sampler=utils.Sampler(top_k=25, temp=0.8), # Kept temp as per original, though often ASR might want lower temp? usage seems to indicate temp=0 for text in original script, but wait...
        # Original: text_sampler=utils.Sampler(top_k=25, temp=0), audio_sampler=utils.Sampler(top_k=250, temp=0.8)
        # I should probably stick to original temps for ASR, text temp 0 is good for deterministic output.
        audio_sampler=utils.Sampler(top_k=250, temp=0.8),
        check=False,
    )
    
    # Re-init generator with correct usage from original script if I made a mistake above
    # Original:
    # text_sampler=utils.Sampler(top_k=25, temp=0),
    # audio_sampler=utils.Sampler(top_k=250, temp=0.8),
    
    gen = models.LmGen(
        model=model,
        max_steps=args.max_steps,
        text_sampler=utils.Sampler(top_k=25, temp=0.0), # Set temp to 0 for text as per original
        audio_sampler=utils.Sampler(top_k=250, temp=0.8),
        check=False,
    )

    block_queue = queue.Queue()

    def audio_callback(indata, _frames, _time, _status):
        block_queue.put(indata.copy())

    print("Recording audio from microphone... Speak to transcribe.")
    
    # We don't need VAD logic if we are just doing continuous ASR or if user didn't ask for it explicitly,
    # but the original script had VAD support. The user said "only do ASR".
    # I will keep it simple: consume audio, print text.
    
    with sd.InputStream(
        channels=1,
        dtype="float32",
        samplerate=24000,
        blocksize=1920,
        callback=audio_callback,
    ):
        while True:
            try:
                block = block_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            block = block[None, :, 0]
            other_audio_tokens = audio_tokenizer.encode_step(block[None, 0:1])
            other_audio_tokens = mx.array(other_audio_tokens).transpose(0, 2, 1)[
                :, :, :other_codebooks
            ]
            
            # Since we are "only doing ASR", we might just want to print what the model predicts for text tokens
            # based on audio input.
            # In the original script, `step` or `step_with_extra_heads` is used.
            # We'll use `step` as we don't need VAD heads if we aren't using VAD logic for control flow.
            
            text_token = gen.step(other_audio_tokens[0])
            text_token = text_token[0].item()
            
            # audio_tokens = gen.last_audio_tokens() # Not used for ASR printing
            
            if text_token not in (0, 3): # 0 is usually pad/unk, 3 might be EOS/special
                _text = text_tokenizer.id_to_piece(text_token)  # type: ignore
                _text = _text.replace("▁", " ")
                print(_text, end="", flush=True)
