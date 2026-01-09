# Battle Camera

Webcam capture with AI transformation for the Battle module.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
python main.py
```

## Features

- 📷 Camera selection dropdown
- 🌙/☀️ Role selector (Nightmare/Dream)
- 🎨 AI transformation with Flux Kontext
- ✂️ Background removal (macOS Vision)
- 📡 WebSocket streaming to battle page

## Structure

```
battle-mlx-cam/
├── main.py              # Entry point with GUI
├── src/
│   ├── camera.py        # Webcam capture
│   ├── transform.py     # fal.ai API
│   ├── background.py    # Background removal
│   └── websocket_client.py  # WS connection
├── requirements.txt
└── .env                 # Your FAL_KEY
```

## Configuration

Add your fal.ai key to `.env`:

```
FAL_KEY=your_key_here
```

Get your key at: https://fal.ai/dashboard/keys
