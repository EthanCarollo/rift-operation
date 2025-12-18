import json
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import rustymimi
import sentencepiece
from huggingface_hub import hf_hub_download
from moshi_mlx import models, utils

class KyutaiSttService:
    def __init__(self, hf_repo="kyutai/stt-1b-en_fr-mlx", local_dir="kyutai-model"):
        self.hf_repo = hf_repo
        self.local_dir = local_dir
        self.model = None
        self.audio_tokenizer = None
        self.text_tokenizer = None
        self.lm_config = None
        self.other_codebooks = 0
        self.is_loaded = False

    def load_model(self):
        if self.is_loaded:
            return

        print(f"Loading Kyutai model from {self.hf_repo}...")
        
        # Download/Load config
        config_path = hf_hub_download(self.hf_repo, "config.json", local_dir=self.local_dir)
        with open(config_path, "r") as fobj:
            config_dict = json.load(fobj)
        
        self.lm_config = models.LmConfig.from_config_dict(config_dict)
        
        # Download/Load weights
        mimi_weights = hf_hub_download(self.hf_repo, config_dict["mimi_name"], local_dir=self.local_dir)
        moshi_name = config_dict.get("moshi_name", "model.safetensors")
        moshi_weights = hf_hub_download(self.hf_repo, moshi_name, local_dir=self.local_dir)
        tokenizer_path = hf_hub_download(self.hf_repo, config_dict["tokenizer_name"], local_dir=self.local_dir)

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
        self.other_codebooks = self.lm_config.other_codebooks
        mimi_codebooks = max(self.lm_config.generated_codebooks, self.other_codebooks)
        self.audio_tokenizer = rustymimi.Tokenizer(mimi_weights, num_codebooks=mimi_codebooks)

        print("Warming up model...")
        self.model.warmup()
        
        self.is_loaded = True
        print("Model loaded.")

    def create_generator(self, max_steps=4096):
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        return models.LmGen(
            model=self.model,
            max_steps=max_steps,
            text_sampler=utils.Sampler(top_k=25, temp=0),
            audio_sampler=utils.Sampler(top_k=250, temp=0.8),
            check=False,
        )

    async def process_audio_chunk(self, data, generator):
        """
        Processes a raw audio chunk and yields transcribed text pieces.
        """
        # Convert to numpy array
        audio_chunk = np.frombuffer(data, dtype=np.float32)
        
        # Adapt input to shape (1, 1, N) for encode_step
        audio_chunk = audio_chunk[None, None, :] 
        
        other_audio_tokens = self.audio_tokenizer.encode_step(audio_chunk)
        other_audio_tokens = mx.array(other_audio_tokens).transpose(0, 2, 1)[:, :, :self.other_codebooks]
        
        # Process each frame separately if multiple frames returned
        num_frames = other_audio_tokens.shape[1]
        transcriptions = []
        
        for frame_idx in range(num_frames):
            # Extract single frame: shape (1, 32) -> what model expects
            single_frame = other_audio_tokens[:, frame_idx:frame_idx+1, :]
            
            # Generate
            text_token = generator.step(single_frame[0])
            text_token = text_token[0].item()
            
            if text_token not in (0, 3):
                text = self.text_tokenizer.id_to_piece(text_token)
                text = text.replace("▁", " ")
                if text:
                    transcriptions.append(text)
        
        return transcriptions
