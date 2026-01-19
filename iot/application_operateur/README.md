# Audio Router - Application Android

📱 Application Android native permettant de router sélectivement l'audio du microphone vers des oreillettes Bluetooth gauche ou droite.

## Fonctionnalités

- 🎤 Capture audio du microphone en temps réel
- 🎧 Routage sélectif vers canal gauche (Personne A) ou droit (Personne C)
- 📊 VU-mètre en temps réel
- 🔵 Indicateur de connexion Bluetooth
- 📳 Retour haptique sur appui
- 🌙 Interface Material Design 3 (thème sombre)

## Prérequis

- Android 8.0 (API 26) minimum
- Écouteurs Bluetooth stéréo (avec canaux L/R séparés)
- Permission microphone

## Installation

### Option 1 : APK précompilé
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Option 2 : Compilation depuis les sources
```bash
./gradlew assembleDebug
```

## Utilisation

1. **Connecter** des écouteurs Bluetooth stéréo
2. **Lancer** l'application et accorder la permission microphone
3. **Appuyer sur ▶️** pour démarrer la capture
4. **Maintenir le bouton GAUCHE** → La personne A (oreillette gauche) entend
5. **Maintenir le bouton DROITE** → La personne C (oreillette droite) entend
6. **Relâcher** → Silence sur les deux canaux

## Architecture Technique

### AudioRouter.kt
- `AudioRecord` : Capture MONO @ 44.1kHz, PCM 16-bit
- `AudioTrack` : Sortie STEREO avec `PERFORMANCE_MODE_LOW_LATENCY`
- Buffers optimisés pour latence < 100ms

### Routage des canaux
```kotlin
// Canal GAUCHE : buffer[i*2] = audio, buffer[i*2+1] = 0
// Canal DROIT  : buffer[i*2] = 0, buffer[i*2+1] = audio
// SILENCE      : tous les samples à 0
```

## Permissions

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.VIBRATE" />
```

## Licence

MIT
