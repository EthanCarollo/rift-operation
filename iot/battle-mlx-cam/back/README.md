# Battle Camera (Headless)

Webcam capture with AI transformation for the Battle module. Runs headless (no GUI), controlled via web API.

## Quick Start

```bash
# Via start_battle.py (recommended - handles everything)
python start_battle.py

# Or manually with conda
conda run -n rift-operation python main_headless.py
```

## Features

- 📷 Dual camera support (Dream/Nightmare roles)
- 🎨 AI transformation with Flux Kontext
- ✂️ Background removal (macOS Vision)
- 📡 WebSocket streaming to battle page
- 🌐 REST API for monitoring (port 5010)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /status` | Battle status |
| `GET /cameras` | List available cameras |

## Socket.io Events

- `camera_frame` - Raw camera frames
- `output_frame` - Transformed frames
- `status` - Battle status updates
- `set_camera` - Set camera for role

## Configuration

Add your fal.ai key to `.env`:

```
FAL_KEY=your_key_here
```

Get your key at: https://fal.ai/dashboard/keys
