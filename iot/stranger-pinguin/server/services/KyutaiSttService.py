import json
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import rustymimi
import sentencepiece
from huggingface_hub import hf_hub_download
from moshi_mlx import models, utils

# ANSI color codes
ORANGE = "\033[38;5;208m"
RESET_COLOR = "\033[0m"

def log_orange(msg: str):
    """Print a message in orange color."""
    print(f"{ORANGE}🟠 {msg}{RESET_COLOR}")

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
        # State for context management
        self._recent_tokens = []
        self._context_invalid = False
        # Buffer for pending audio chunks during reset
        self._pending_audio_chunks = []

    def load_model(self):
        """Load the model from scratch (hard reset)."""
        # Reset loaded flag to allow reloading
        self.is_loaded = False
        
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
        self._recent_tokens.clear()
        self._context_invalid = False
        print("Model loaded.")

    def create_generator(self, max_steps=4096):
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Clear context state when creating new generator
        self._recent_tokens.clear()
        self._context_invalid = False
        # Note: Don't clear pending chunks here - they'll be processed by caller
            
        return models.LmGen(
            model=self.model,
            max_steps=max_steps,
            text_sampler=utils.Sampler(top_k=25, temp=0),
            audio_sampler=utils.Sampler(top_k=250, temp=0.8),
            check=False,
        )

    def _check_loop_detected(self, piece: str) -> bool:
        """Check if we're in a loop (same piece repeated 6 times)."""
        self._recent_tokens.append(piece)
        if len(self._recent_tokens) > 8:
            self._recent_tokens.pop(0)
        
        if len(self._recent_tokens) >= 6:
            if all(p == piece for p in self._recent_tokens[-6:]):
                return True
        return False

    def get_pending_chunks(self) -> list:
        """Get and clear pending audio chunks that need reprocessing."""
        chunks = self._pending_audio_chunks.copy()
        self._pending_audio_chunks.clear()
        return chunks

    def has_pending_chunks(self) -> bool:
        """Check if there are pending chunks to process."""
        return len(self._pending_audio_chunks) > 0

    async def process_audio_chunk(self, data, generator):
        """
        Processes a raw audio chunk and yields transcribed text pieces.
        Raises ContextOverflowError if context needs to be reset.
        """
        # If context was marked invalid, signal caller to recreate generator
        if self._context_invalid:
            self._context_invalid = False
            # Save this chunk for reprocessing after reset
            self._pending_audio_chunks.append(data)
            raise ContextOverflowError("Context was invalidated, needs reset")

        try:
            # Convert to numpy array
            audio_chunk = np.frombuffer(data, dtype=np.float32).copy()
            
            # Adapt input to shape (1, 1, N) for encode_step
            audio_chunk = audio_chunk[None, None, :] 
            
            other_audio_tokens = self.audio_tokenizer.encode_step(audio_chunk)
            other_audio_tokens = mx.array(other_audio_tokens).transpose(0, 2, 1)[:, :, :self.other_codebooks]
            
            # Process each frame separately if multiple frames returned
            num_frames = other_audio_tokens.shape[1]
            transcriptions = []
            
            for frame_idx in range(num_frames):
                # Preventative reset: check if approaching context limit
                if hasattr(generator, 'step_idx') and hasattr(generator, 'max_steps'):
                    if generator.step_idx >= generator.max_steps - 32:
                        log_orange(f"[STT] Context approaching limit (step_idx: {generator.step_idx}/{generator.max_steps}). Resetting...")
                        self._context_invalid = True
                        self._pending_audio_chunks.append(data)  # Save for reprocessing
                        raise ContextOverflowError("Approaching context limit, needs reset")
                
                # Extract single frame: shape (1, 32) -> what model expects
                single_frame = other_audio_tokens[:, frame_idx:frame_idx+1, :]
                
                # Generate
                text_token = generator.step(single_frame[0])
                text_token = text_token[0].item()
                
                if text_token not in (0, 3):
                    text = self.text_tokenizer.id_to_piece(text_token)
                    text = text.replace("▁", " ")
                    if text:
                        # Check for loop (repetition bug)
                        if self._check_loop_detected(text):
                            log_orange(f"[STT] Loop detected ('{text}' x6). Hard resetting model...")
                            self._context_invalid = True
                            self._pending_audio_chunks.append(data)  # Save for reprocessing
                            self.load_model()  # Hard reset
                            raise ContextOverflowError("Loop detected, model reloaded")
                        
                        transcriptions.append(text)
            
            return transcriptions
            
        except ContextOverflowError:
            raise  # Re-raise our custom exception
        except Exception as e:
            msg = str(e)
            # Handle known context overflow errors from Kyutai
            if "narrow invalid args" in msg or "start + len > dim_len" in msg:
                log_orange(f"[STT] Context full! Performing HARD RESET...")
                self._context_invalid = True
                self._pending_audio_chunks.append(data)  # Save for reprocessing
                self.load_model()  # Hard reset - reload model
                raise ContextOverflowError(f"Context overflow: {msg}")
            # Re-raise other exceptions
            raise


class ContextOverflowError(Exception):
    """Raised when Kyutai context is full and needs reset."""
    pass
