✅ Authentification
✅ Dashboard client
✅ Profil client
✅ Gestion des clients par l’admin
✅ Création d’un client
✅ Modification d’un client
✅ Activation / désactivation
✅ Gestion de plusieurs compteurs
✅ Recharge du solde en kWh
✅ PZEM-004T
✅ Mesures ESP32 → Django
✅ Affichage temps réel
✅ Historique
✅ Dashboard administrateur

## Connexion ESP32 à PythonAnywhere

Le firmware `esp32_pzem_004T_v10` envoie ses requêtes en HTTPS vers
`https://tsito.pythonanywhere.com`. L'adresse de base est définie une seule
fois dans `API_BASE_URL` du fichier `.ino`; les trois routes attendues sont :

- `POST /api/pzem/mesure/` avec `device_id`, `tension`, `courant`,
  `puissance` et `energie` numériques ;
- `GET /api/esp32/etat/<device_id>/` renvoyant notamment `solde`,
  `autorisation` et `contacteur` ;
- `POST /api/esp32/heartbeat/` avec `device_id` et `relais_on` booléen JSON.

Les réponses d'erreur gardent `success` et `message` à la racine pour
compatibilité et ajoutent `error.code`, `error.message` et
`error.retryable`. Les routes ESP32/PZEM continuent de répondre en JSON; le
firmware journalise également le code HTTP et le corps d'erreur reçu.

Le firmware vérifie TLS avec le certificat racine ISRG Root X1 (Let's Encrypt)
et n'utilise pas de connexion HTTPS non vérifiée. Si l'autorité de
certification présentée par l'hôte change, mettre à jour `API_ROOT_CA`.

Dans l'environnement PythonAnywhere, configurer `DJANGO_SECRET_KEY` avec une
clé secrète privée, `DJANGO_DEBUG=False` et
`DJANGO_ALLOWED_HOSTS=tsito.pythonanywhere.com`. `ALLOWED_HOSTS` inclut déjà
cet hôte par défaut, tout en restant configurable par variable
d'environnement.

### Fichiers statiques sur PythonAnywhere

La destination de collecte est `staticfiles/` (`STATIC_ROOT`). Après chaque
mise à jour du code, lancer dans une console Bash PythonAnywhere depuis le
répertoire du projet :

```bash
python manage.py collectstatic --noinput
```

Dans l'onglet **Web > Static files**, créer le mappage `/static/` vers le
chemin absolu `.../gestion_electricite/staticfiles` de ce projet. Puis
recharger l'application Web PythonAnywhere.



CABLAGE:

| Élément             |   GPIO |
| ------------------- | -----: |
| PZEM RX             | GPIO16 |
| PZEM TX             | GPIO17 |
| LCD SDA             | GPIO21 |
| LCD SCL             | GPIO22 |
| Relais              | GPIO25 |
| 🔊 Buzzer actif 5 V | GPIO26 |
| 🟢 LED verte        | GPIO27 |
| 🟠 LED orange       | GPIO32 |
| 🔴 LED rouge        | GPIO33 |


<!-- ++++++++++++ -->
Solde > 2 kWh
      ↓
contacteur = ON
      ↓
🟢 LED + silence

<!-- ----------- -->

0 < Solde ≤ 2 kWh
      ↓
contacteur reste selon Django
      ↓
🟠 LED + bip
<!-- ------------ -->

Solde = 0
      ↓
Django → contacteur = OFF
      ↓
ESP32 → relais OFF
      ↓
🔴 LED + plusieurs bips
<!-- ++++++++++++ -->



Plan de travail
Dashboard administrateur — priorité
statistiques en temps réel
clients connectés
compteurs
solde total
consommation
état ESP32
état contacteur
actualisation automatique
Gestion des clients
recherche instantanée
filtres
activation/désactivation
accès rapide aux compteurs
modification simple
Gestion des compteurs
recherche par nom / device_id
solde
recharge
autorisation
contacteur
connexion ESP32
dernières mesures PZEM
Historique dynamique
ON/OFF
recharges
consommations
coupures automatiques
filtres par compteur et période
Communication ESP32 ↔ Django
état réel
dernière connexion
gestion des erreurs
synchronisation automatique
ESP32
PZEM
LCD
relais/contacteur
LED
buzzer
synchronisation du solde et de l'autorisation
Méthode

On fait un seul fichier à la fois :

fichier → code complet → test → validation → fichier suivant.

Et surtout, je ne touche pas aux pages déjà validées sans nécessité.


ESP32 → heartbeat → Django        ✅
Django → état → ESP32             ✅
Relais réel OFF                   ✅
Autorisation Django = true        ✅
Contacteur Django = false         ✅
Solde = 10.0 kWh                  ✅

Le cycle complet est donc maintenant :
             ┌────────────────────┐
             │      DJANGO        │
             │                    │
             │ Autorisation       │
             │ Solde              │
             │ Contacteur ON/OFF  │
             └─────────┬──────────┘
                       │
                 GET état / 2s
                       ↓
             ┌────────────────────┐
             │       ESP32        │
             │                    │
             │ décide le relais   │
             └─────────┬──────────┘
                       │
                       ↓
                  GPIO25
                       │
                       ↓
                  RELAIS ON/OFF
                       │
                 état réel
                       │
                       ↓
             POST heartbeat / 2s
                       │
                       ↓
             ┌────────────────────┐
             │      DJANGO        │
             │ état réel relais   │
             └────────────────────┘

✅ Déjà terminé / fonctionnel
1 Django + base de données
Clients/profils
Compteurs
Mesures PZEM
Historique des commandes
Mouvements de solde
2 API ESP32 / PZEM
Réception des mesures PZEM
Enregistrement des mesures
Calcul de consommation
Déduction du solde
Gestion autorisation/contacteur
3 Communication ESP32 ↔ Django
Heartbeat ESP32
État du contacteur
État connecté/déconnecté
device_id
4 Dashboard client
Solde
Consommation
Dernières mesures
Actualisation automatique
Données temps réel
5 Dashboard administrateur
Liste des clients
Liste des compteurs
Solde total
Consommation
Compteurs connectés/coupés
Actualisation automatique
6 Page des compteurs d'un client
Exemple :
/admin-dashboard/clients/5/compteurs/
API spécifique au client créée
Les statistiques du haut sont maintenant correctes ✅
7 JavaScript temps réel
Détection automatique de l'ID client dans l'URL
Utilisation de l'API spécifique :
/api/admin/clients/<client_id>/compteurs/
Correction du calcul des statistiques


| Fonction                       | État actuel              |
| ------------------------------ | ------------------------ |
| 👤 Gestion des clients         | 🟡 À vérifier            |
| ➕ Ajouter un compteur          | 🟡 À vérifier            |
| ✏️ Modifier un compteur        | 🟡 À vérifier            |
| 🔌 ON/OFF contacteur           | 🔴 À vérifier/corriger   |
| 💰 Recharger un compteur       | 🟡 À vérifier            |
| 📊 Dashboard admin             | 🟡 À vérifier            |
| 👤 Dashboard client            | 🟡 À vérifier            |
| ⚡ PZEM → Django                | 🟢 Fonctionne déjà       |
| 📡 ESP32 → Django              | 🟢 Fonctionne déjà       |
| 🔄 Temps réel                  | 🟢 Fonctionne en partie  |
| 📟 Carte compteur client       | 🟡 À finaliser           |
| 💳 Solde / consommation        | 🟡 À tester complètement |
| ✂️ Coupure automatique         | 🟡 À tester              |
| 🔌 Réactivation après recharge | 🟡 À tester              |
| 📜 Historique des mouvements   | 🟡 À vérifier            |
| 📜 Historique ON/OFF           | 🟡 À vérifier            |
| 🔐 Autorisation / sécurité     | 🟡 À vérifier            |
| 📱 Responsive/mobile           | 🟡 À vérifier            |
| 🤖 Firmware ESP32 final        | 🟡 À valider             |
| 🧪 Tests complets du système   | 🔴 À faire               |


🔧 Notre méthode maintenant

On va faire exactement ceci :

Étape 1 — Ajouter compteur
→ test réel

Étape 2 — Modifier compteur
→ test réel

Étape 3 — ON/OFF contacteur
→ test réel

Étape 4 — Recharge
→ test réel

Étape 5 — Consommation PZEM → diminution du solde
→ test réel

Étape 6 — Solde épuisé → coupure automatique
→ test réel

Étape 7 — Recharge → réactivation
→ test réel

Étape 8 — Historique
→ vérification

Étape 9 — ESP32
→ validation complète

Étape 10 — Test final de toute la chaîne