#!/usr/bin/env python3
"""
Battle Camera - Headless Entry Point.
Runs without tkinter GUI, controlled via web API.
"""
import signal
import sys
from dotenv import load_dotenv

from src.Core import init_service, get_service
# Use new BattleWebServer from Core
from src.Core import BattleWebServer

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
    
    # Initialize battle service
    service = init_service()
    
    # Start the service
    service.start()
    
    # Start web server
    print("[Headless] Starting web server on http://0.0.0.0:5010")
    
    # Instantiate BattleWebServer with service provider callback
    web_server = BattleWebServer(service_provider=get_service)
    web_server.start(host='0.0.0.0', port=5010)


if __name__ == "__main__":
    main()
