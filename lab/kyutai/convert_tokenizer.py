import sentencepiece as spm
import json
import os

model_dir = "rift-pinguin/Moshi/kyutai-model"
model_path = os.path.join(model_dir, "tokenizer_en_fr_audio_8000.model")
json_path = os.path.join(model_dir, "tokenizer.json")

if not os.path.exists(model_path):
    print(f"Error: {model_path} not found")
    exit(1)

sp = spm.SentencePieceProcessor()
sp.load(model_path)

vocab = {}
for i in range(sp.get_piece_size()):
    vocab[i] = sp.id_to_piece(i)

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

print(f"Exported tokenizer vocabulary to {json_path}")
