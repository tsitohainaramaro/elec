from django.urls import path

from . import views


# ============================================================
# NOM DE L'APPLICATION
# ============================================================

app_name = "compteur"


urlpatterns = [

    # ========================================================
    # PAGE PUBLIQUE
    # ========================================================
    path(
        "",
        views.visiteur,
        name="visiteur"
    ),

    # ========================================================
    # ESPACE CLIENT
    # ========================================================

    # Tableau de bord principal du client
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # Connexion
    path(
        "connexion/",
        views.connexion,
        name="connexion"
    ),

    # Déconnexion
    path(
        "deconnexion/",
        views.deconnexion,
        name="deconnexion"
    ),

    # Profil du client
    path(
        "profil/",
        views.profil,
        name="profil"
    ),

    # Page de consommation
    path(
        "consommation/",
        views.consommation,
        name="consommation"
    ),

    # Détails d'un compteur
    path(
        "compteur/<int:compteur_id>/",
        views.compteur_detail,
        name="compteur_detail"
    ),


    # ========================================================
    # ESPACE ADMINISTRATEUR
    # ========================================================

    # Tableau de bord administrateur
    path(
        "admin-dashboard/",
        views.dashboard_admin,
        name="dashboard_admin"
    ),

    # Liste des clients
    path(
        "admin-dashboard/clients/",
        views.clients_admin,
        name="clients_admin"
    ),

    # Ajouter un nouveau client
    path(
        "admin-dashboard/clients/nouveau/",
        views.client_create_admin,
        name="client_create_admin"
    ),

    # Modifier un client existant
    path(
        "admin-dashboard/clients/<int:client_id>/modifier/",
        views.client_edit_admin,
        name="client_edit_admin"
    ),

    # Activer ou désactiver un client
    path(
        "admin-dashboard/clients/<int:client_id>/activer/",
        views.client_toggle_admin,
        name="client_toggle_admin"
    ),

    # ========================================================
    # COMPTEURS D'UN CLIENT
    # ========================================================

    # --------------------------------------------------------
    # Ajouter un compteur pour un client

    path(
        "admin-dashboard/clients/<int:client_id>/compteurs/nouveau/",
        views.client_compteur_create_admin,
        name="client_compteur_create_admin"
    ),



    # ========================================================
    # MODIFIER UN COMPTEUR
    # ========================================================

    path(
        "admin-dashboard/clients/<int:client_id>/compteurs/<int:compteur_id>/modifier/",
        views.client_compteur_edit_admin,
        name="client_compteur_edit_admin"
    ),



    # ========================================================
    # CHANGER L'ÉTAT DU CONTACTEUR
    # ========================================================

    path(
        "admin-dashboard/clients/<int:client_id>/compteurs/<int:compteur_id>/contacteur/",
        views.client_compteur_toggle_contacteur_admin,
        name="client_compteur_toggle_contacteur_admin"
    ),


    # --------------------------------------------------------
    # Afficher les compteurs d'un client
    # --------------------------------------------------------
    path(
        "admin-dashboard/clients/<int:client_id>/compteurs/",
        views.client_compteurs_admin,
        name="client_compteurs_admin"
    ),

    # Liste générale de tous les compteurs
    path(
        "admin-dashboard/compteurs/",
        views.compteurs_admin,
        name="compteurs_admin"
    ),

    # Recharger le solde d'un compteur
    path(
        "admin-dashboard/compteurs/<int:compteur_id>/recharger/",
        views.recharger_compteur_admin,
        name="recharger_compteur_admin"
    ),

    # Historique des commandes
    path(
        "admin-dashboard/historique/",
        views.historique_admin,
        name="historique_admin"
    ),


    # ========================================================
    # API ESP32 / PZEM
    # ========================================================

    # Réception des mesures envoyées par l'ESP32
    path(
        "api/pzem/mesure/",
        views.api_pzem_mesure,
        name="api_pzem_mesure"
    ),

    # api_esp32_etat 
    path(
        "api/esp32/etat/<str:device_id>/",
        views.api_esp32_etat,
        name="api_esp32_etat"
    ),

    # heartbeat
    path(
        "api/esp32/heartbeat/",
        views.api_esp32_heartbeat,
        name="api_esp32_heartbeat"
    ),

    # Données temps réel utilisées par le dashboard
    path(
        "api/temps-reel/",
        views.api_temps_reel,
        name="api_temps_reel"
    ),

    # ========================================================
    # API ADMIN - CLIENTS
    # ========================================================


    path(
        "api/admin/clients/",
        views.api_admin_clients,
        name="api_admin_clients"
    ),

    # ========================================================
    # API ADMIN - COMPTEUR
    # ========================================================

    path(
        "api/admin/compteurs/",
        views.api_admin_compteurs,
        name="api_admin_compteurs"
    ),


    path(
        "api/admin/clients/<int:client_id>/compteurs/",
        views.api_client_compteurs_admin,
        name="api_client_compteurs_admin"
    ),
]