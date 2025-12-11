# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network

NEED_WIFI = True

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)  # Crée un objet WLAN en mode STA
    if not wlan.isconnected():  # Vérifie si déjà connecté
        wlan.active(True)  # Active l'interface STA
        wlan.connect(ssid, password)  # Tente de se connecter au réseau
        print('Connexion au réseau', ssid)
        while not wlan.isconnected():
            pass  # Attendre jusqu'à la connexion
    print('Configuration réseau :', wlan.ifconfig())

# Remplacer 'your-ssid' par votre SSID Wi-Fi et 'your-password' par votre mot de passe Wi-Fi
if NEED_WIFI:
    ssid = 'Freebox-A01429'
    password = '5f4ktqwkwkqdx62rqcdwxs'
    connect_wifi(ssid, password)
