# Battle Camera

Webcam capture with AI transformation for the Battle module.

## Features

- 📷 Webcam capture via OpenCV
- 🎨 AI transformation with [fal.ai Flux Kontext](https://fal.ai/models/fal-ai/flux-kontext/dev) (~3s)
- ✂️ Background removal with macOS Vision (local, ultra-fast)
- 📡 Real-time streaming via WebSocket to the battle page

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.sample .env
# Edit .env and add your FAL_KEY
```

## Usage

### Continuous Mode (default)

Captures and transforms every 3 seconds:

```bash
python battle_camera.py \
  --prompt "Steel katana sword cartoon style" \
  --role nightmare \
  --interval 3
```

### Single Capture

```bash
python battle_camera.py --once --prompt "Magic shield" --role dream
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--prompt` | `-p` | `"Steel katana sword..."` | Transformation prompt |
| `--role` | `-r` | `nightmare` | Agent role (`dream` or `nightmare`) |
| `--camera` | `-c` | `0` | Camera index |
| `--interval` | `-i` | `3.0` | Capture interval in seconds |
| `--once` | - | `false` | Single capture mode |

## Architecture

```
Webcam → Capture → fal.ai → Background Removal → WebSocket → battle.vue
  │                  │              │                │
  └─ OpenCV          └─ ~3s         └─ Vision        └─ PNG base64
```

## Files

- `battle_camera.py` - Main script
- `image_to_art_fal_flux_kontext_dev.py` - Reference implementation
- `requirements.txt` - Python dependencies
- `.env.sample` - Environment variables template
