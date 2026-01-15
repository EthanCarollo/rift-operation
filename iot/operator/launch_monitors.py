#!/usr/bin/env python3
"""
Script de lancement des fenêtres de monitoring en mode kiosk.

Lance 3 fenêtres de navigateur :
- 2 fenêtres pour les caméras (dream & nightmare)
- 1 fenêtre pour la mission

Toutes les fenêtres se ferment avec Ctrl+C.
"""

import subprocess
import signal
import sys
import time
import os
import json

# Configuration
NUXT_PORT = 3000
BASE_URL = f"http://localhost:{NUXT_PORT}"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monitors_config.json")
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Définition des écrans (à ajuster selon ta config)
# Écran 0 = principal, Écran 1 = secondaire à droite, Écran 2 = si tu en as un 3ème
SCREENS = {
    0: {"x": 0, "y": 0, "width": 1920, "height": 1080},
    1: {"x": 1920, "y": 0, "width": 1920, "height": 1080},
    2: {"x": 3840, "y": 0, "width": 1920, "height": 1080},
}

# Fenêtres à lancer
WINDOW_DEFINITIONS = [
    {"name": "Dream Camera", "url": f"{BASE_URL}/monitor?camera=dream"},
    {"name": "Nightmare Camera", "url": f"{BASE_URL}/monitor?camera=nightmare"},
    {"name": "Mission", "url": f"{BASE_URL}/mission"},
]

# Liste des processus lancés
processes = []


def cleanup(signum=None, frame=None):
    """Ferme tous les processus Chrome lancés."""
    print("\n🛑 Fermeture des fenêtres...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
    print("✅ Toutes les fenêtres fermées.")
    sys.exit(0)


def load_config() -> dict | None:
    """Charge la configuration depuis le fichier JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_config(config: dict):
    """Sauvegarde la configuration dans le fichier JSON."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"💾 Configuration sauvegardée dans {CONFIG_FILE}")


def create_config() -> dict:
    """Crée une nouvelle configuration interactivement."""
    print("\n📝 Configuration des fenêtres")
    print("-" * 40)
    print("Écrans disponibles: 0, 1, 2")
    print()
    
    config = {"windows": []}
    
    for window_def in WINDOW_DEFINITIONS:
        while True:
            try:
                screen_choice = input(f"  {window_def['name']} → Écran (0/1/2): ").strip()
                screen_num = int(screen_choice)
                if screen_num not in SCREENS:
                    print("    ❌ Choisis 0, 1 ou 2")
                    continue
                
                config["windows"].append({
                    "name": window_def["name"],
                    "url": window_def["url"],
                    "screen": screen_num,
                })
                break
            except ValueError:
                print("    ❌ Entre un nombre: 0, 1 ou 2")
            except KeyboardInterrupt:
                print("\n❌ Configuration annulée")
                sys.exit(0)
    
    save_config(config)
    return config


def display_config(config: dict):
    """Affiche la configuration actuelle."""
    print("\n📋 Configuration actuelle:")
    print("-" * 40)
    for w in config["windows"]:
        print(f"  • {w['name']} → Écran {w['screen']}")
    print()


def open_chrome_kiosk(name: str, url: str, screen: int):
    """
    Ouvre une fenêtre Chrome en mode kiosk sur l'écran spécifié.
    """
    screen_config = SCREENS[screen]
    
    # Arguments Chrome pour mode kiosk
    args = [
        CHROME_PATH,
        f"--user-data-dir=/tmp/chrome_kiosk_{name.replace(' ', '_')}",
        "--kiosk",  # Mode kiosk = plein écran sans interface
        f"--window-position={screen_config['x']},{screen_config['y']}",
        f"--window-size={screen_config['width']},{screen_config['height']}",
        "--disable-extensions",
        "--disable-sync",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--disable-restore-session-state",
        url,
    ]
    
    print(f"🚀 {name} → Écran {screen} ({url})")
    
    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    processes.append(proc)
    return proc


def main():
    print("=" * 50)
    print("🖥️  Rift Operation - Lanceur de Moniteurs")
    print("=" * 50)
    print(f"📡 Base URL: {BASE_URL}")
    
    # Vérifie que Chrome est installé
    if not os.path.exists(CHROME_PATH):
        print(f"❌ Chrome non trouvé: {CHROME_PATH}")
        sys.exit(1)
    
    # Charge ou crée la configuration
    existing_config = load_config()
    
    if existing_config:
        display_config(existing_config)
        print("Que veux-tu faire?")
        print("  [1] Utiliser cette configuration")
        print("  [2] Créer une nouvelle configuration")
        print()
        
        try:
            choice = input("Choix (1/2): ").strip()
        except KeyboardInterrupt:
            print("\n❌ Annulé")
            sys.exit(0)
        
        if choice == "2":
            config = create_config()
        else:
            config = existing_config
    else:
        print("\n⚠️  Aucune configuration trouvée")
        config = create_config()
    
    # Configure le handler pour Ctrl+C
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    print()
    print("=" * 50)
    print("🚀 Lancement des fenêtres en mode kiosk...")
    print("=" * 50)
    
    # Lance chaque fenêtre
    for window in config["windows"]:
        open_chrome_kiosk(
            name=window["name"],
            url=window["url"],
            screen=window["screen"],
        )
        time.sleep(0.5)
    
    print()
    print("=" * 50)
    print("✅ Toutes les fenêtres sont lancées!")
    print("🔄 Ctrl+C pour tout fermer")
    print("=" * 50)
    
    # Attend indéfiniment
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
