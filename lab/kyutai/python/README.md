# Kyutai Swift Runner

Ce dossier contient un squelette de projet **Swift** pour exécuter le modèle Kyutai en utilisant le framework **MLX** d'Apple (optimisé pour Apple Silicon).

## Prérequis

- macOS 14+ (Sonoma)
- Xcode Command Line Tools installés (`xcode-select --install`)
- Swift 5.9+

## Installation & Exécution

1.  **Télécharger le modèle** (si ce n'est pas déjà fait) :
    Assurez-vous d'avoir exécuté le script Python dans le dossier parent qui télécharge les poids dans `../kyutai_model`.
    ```bash
    cd ..
    python kyutai_test.py
    ```

2.  **Lancer le projet Swift** :
    Allez dans le dossier `swift_app` et lancez via `swift run`.
    
    ```bash
    cd swift_app
    swift run
    ```

    *La première exécution va télécharger les dépendances `mlx-swift`, ce qui peut prendre une minute.*

## Structure du Projet

- `Package.swift` : Configuration des dépendances (inclut `mlx-swift`).
- `Sources/KyutaiRunner/main.swift` : Point d'entrée de l'application.

## Note sur le Portage

Ce projet configure l'environnement MLX pour Swift. Cependant, exécuter le modèle Moshi complet demande de porter l'architecture du réseau de neurones (définie en Python/PyTorch) vers des classes Swift `nn.Module`.

Les poids téléchargés (`.safetensors`) sont compatibles et peuvent être chargés avec `MLX.load()`.
