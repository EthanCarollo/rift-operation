import json
import mlx.core as mx
import mlx.nn as nn
import rustymimi
import sentencepiece
from huggingface_hub import hf_hub_download
from moshi_mlx import models, utils
import numpy as np

class KyutaiService:
    def __init__(self):
        self.model = None
        self.audio_tokenizer = None
        self.text_tokenizer = None
        self.lm_config = None
        self.other_codebooks = 0
        self.is_loaded = False

    def load_model(self):
        if self.is_loaded:
            return

        print("Loading Kyutai model...")
        hf_repo = "kyutai/stt-1b-en_fr-mlx"
        local_dir = "kyutai-model"
        
        # Download/Load config
        config_path = hf_hub_download(hf_repo, "config.json", local_dir=local_dir)
        with open(config_path, "r") as fobj:
            config_dict = json.load(fobj)
        
        self.lm_config = models.LmConfig.from_config_dict(config_dict)
        
        # Download/Load weights
        mimi_weights = hf_hub_download(hf_repo, config_dict["mimi_name"], local_dir=local_dir)
        moshi_name = config_dict.get("moshi_name", "model.safetensors")
        moshi_weights = hf_hub_download(hf_repo, moshi_name, local_dir=local_dir)
        tokenizer_path = hf_hub_download(hf_repo, config_dict["tokenizer_name"], local_dir=local_dir)

        # Initialize Model
        self.model = models.Lm(self.lm_config)
        self.model.set_dtype(mx.bfloat16)
        
        # Quantization check
        if moshi_weights.endswith(".q4.safetensors"):
            nn.quantize(self.model, bits=4, group_size=32)
        elif moshi_weights.endswith(".q8.safetensors"):
            nn.quantize(self.model, bits=8, group_size=64)

        print(f"Loading weights from {moshi_weights}")
        self.model.load_weights(moshi_weights, strict=True)

        print(f"Loading tokenizer from {tokenizer_path}")
        self.text_tokenizer = sentencepiece.SentencePieceProcessor(tokenizer_path)

        print(f"Loading audio tokenizer from {mimi_weights}")
        generated_codebooks = self.lm_config.generated_codebooks
        other_codebooks_count = self.lm_config.other_codebooks
        self.other_codebooks = other_codebooks_count
        mimi_codebooks = max(generated_codebooks, other_codebooks_count)
        self.audio_tokenizer = rustymimi.Tokenizer(mimi_weights, num_codebooks=mimi_codebooks)

        print("Warming up model...")
        self.model.warmup()
        self.is_loaded = True
        print("Kyutai Service Ready.")

    def create_generator(self):
        """Creates a new generator session for a client"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
            
        return models.LmGen(
            model=self.model,
            max_steps=4096,
            text_sampler=utils.Sampler(top_k=25, temp=0),
            audio_sampler=utils.Sampler(top_k=250, temp=0.8),
            check=False,
        )

    def process_audio_chunk(self, generator, audio_chunk: np.ndarray):
        """
        Process a chunk of audio and return generated text token (if any).
        Audio chunk expected as float32 in shape (N,) or (1, N).
        """
        # Ensure shape (1, 1, N) for tokenizer
        if audio_chunk.ndim == 1:
            audio_chunk = audio_chunk[None, None, :]
        elif audio_chunk.ndim == 2:
            audio_chunk = audio_chunk[None, :]

        other_audio_tokens = self.audio_tokenizer.encode_step(audio_chunk)
        
        # Transpose/Select codebooks
        other_audio_tokens = mx.array(other_audio_tokens).transpose(0, 2, 1)[:, :, :self.other_codebooks]
        
        # Generate
        # Vad logic is internal to the model if enabled, but we use standard step here 
        # unless we explicitly want VAD handling on the output side too.
        # User mentioned "vad is already in the model", implying we might trust the model tokens 
        # or logic. kyutai_test.py has specific VAD checking logic (step_with_extra_heads).
        # We will use simple step for now as we want transcription.
        
        text_token = generator.step(other_audio_tokens[0])
        text_token = text_token[0].item()
        
        return text_token

    def decode_token(self, token_id: int):
        if token_id in (0, 3): # Pad/EOS
            return None
        text = self.text_tokenizer.id_to_piece(token_id)
        return text.replace("▁", " ")

# Singleton instance
kyutai_service = KyutaiService()
