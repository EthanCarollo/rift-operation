# Guide de lancement - Expérience Depth Dream

Ce guide décrit la procédure complète pour lancer l'expérience Depth Dream avec les Sphero.

## Prérequis

- 3 Sphero (SB-08C9, SB-1219, SB-2020)
- ESP32 (Xilo) branché
- Serveur WebSocket actif sur `192.168.10.7:8000`
- Dépendances Python installées (`pip install -r requirements.txt`)

## Procédure de lancement

### 1. Lancer depth_game.py

Dans le dossier ESP Dream :

```bash
cd /iot/esp/src/Core/Controller/Depth/Dream
python depth_game.py
```

Ce script gère automatiquement la connexion aux Sphero et l'ensemble de l'expérience Dream.

### 3. Attendre la connexion des 3 Sphero

**Important :** Attendre que les 3 Sphero soient connectés avant de continuer.

Vous verrez dans le terminal :
- ✅ **Indicateurs verts** pour chaque Sphero connecté
- **OU** message dans le terminal confirmant : **"3 Sphero connectés"**
2
**Mapping des Sphero :**
- `SB-08C9` → Note 1 (DO)
- `SB-1219` → Note 2 (RE)
- `SB-2020` → Note 3 (MI)

### 3. Redémarrer l'ESP32 (Xilo)

Une fois les 3 Sphero connectés :
1. **Débrancher** le Xilo (ESP32) du port USB
2. **Rebrancher** le Xilo pour le relancer

⚠️ Cette étape est **cruciale** pour réinitialiser l'ESP et synchroniser l'ensemble du système.

### 4. Envoyer la commande de démarrage

Une fois que tout est opérationnel, envoyer la commande :

```json
{
  "rift_part_count": 2
}
```

Cette commande peut être envoyée via :
- L'interface web de contrôle : `http://192.168.10.7:8000/clients.html`
- Une commande WebSocket directe au serveur

Le script `depth_game.py` attendra que `rift_part_count == 2` avant de démarrer l'expérience.

### 5. Accéder à l'écran Dream

L'écran de visualisation Dream est accessible via le projet website à l'URL :

```
http://localhost:3000/depth-diapo
```

Le fichier source se trouve dans : `/website/app/pages/depth-diapo.vue`

Pour lancer le site web (si pas déjà lancé) :
```bash
cd /website
npm run dev
```

## Configuration

### WebSocket
- **URL:** `ws://192.168.10.7:8000/ws`
- **Role:** `dream`
- **Device ID:** `macbook_pro_1`

### Partition
La partition prédéfinie :
```python
[1, 2, 3, 4, 5, 6, 5, 4, 5, 1, 3, 2, 2, 3, 1, 2, 5, 6, 4, 5]
```

## Vérification du bon fonctionnement

✅ **Checklist :**
- [ ] Projet website lancé (`npm run dev` dans `/website`)
- [ ] depth_game.py en cours d'exécution
- [ ] 3 Sphero connectés (indicateurs verts ou message terminal)
- [ ] ESP32 redémarré après connexion des Sphero
- [ ] `rift_part_count = 2` envoyé via l'interface
- [ ] Écran Dream accessible à `http://localhost:3000/depth-diapo`

## Dépannage

### Les Sphero ne se connectent pas
- Vérifier que les Sphero sont allumés et chargés
- Redémarrer le Bluetooth sur le Mac
- Relancer `depth_game.py`
- Vérifier dans `controllerRaspberry.py` que les noms correspondent

### L'ESP ne répond pas
- Vérifier la connexion USB du Xilo
- Débrancher/rebrancher le Xilo
- Vérifier les logs du serveur WebSocket à `192.168.10.7:8000`
- Vérifier que l'ESP est bien flashé avec le bon code

### L'écran Dream ne s'affiche pas
- Vérifier que le projet website est lancé (`cd website && npm run dev`)
- Accéder à `http://localhost:3000/depth-diapo`
- Vérifier que `rift_part_count = 2` a bien été envoyé
- Consulter la console du navigateur pour les erreurs WebSocket

### Le jeu logs de `depth_game.py`, vérifier :
  - Message : `⏳ Waiting for start conditions...`
  - Valeur de `RiftPartCount`
- Si coincé, envoyer à nouveau `rift_part_count = 2`

## Architecture

Tout le code de l'expérience Depth Dream se trouve dans :

```
esp/src/Core/Controller/Depth/Dream/
  ├─ depth_game.py           → Script principal Dream (gère tout)
  ├─ controllerRaspberry.py  → Contrôleur Sphero
  ├─ DreamLedController.py   → Contrôleur LED
  └─ requirements.txt        → Dépendances Python
```

L'écran de visualisation se trouve dans :
```
website/app/pages/depth-diapo.vue  → Interface Dream
  → Accessible à : http://localhost:3000/depth-diapo
```
/public/tools/             → Écran Dream