#!/usr/bin/env python3
"""
Battle Camera - Headless Entry Point.
Runs without tkinter GUI, controlled via web API.
"""
import signal
import sys
from dotenv import load_dotenv

from src.battle_service import init_service, get_service
from src.web_server import start_server_headless

load_dotenv()


def signal_handler(sig, frame):
    """Handle shutdown signal."""
    print("\n[Headless] Shutting down...")
    service = get_service()
    if service:
        service.cleanup()
    sys.exit(0)


def main():
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("[Headless] Starting Battle Camera (Headless Mode)...")
    
    # Initialize battle service with default cameras
    # nightmare=0 (first camera), dream=1 (second camera)
    service = init_service(nightmare_cam=0, dream_cam=1)
    
    # Start the service (begins monitoring WebSocket)
    service.start()
    
    # Start web server (blocking)
    print("[Headless] Starting web server on http://0.0.0.0:5010")
    start_server_headless(host='0.0.0.0', port=5010)


if __name__ == "__main__":
    main()
