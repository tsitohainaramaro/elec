from django.urls import path

from . import views


app_name = "compteur"


urlpatterns = [

    # ============================================================
    # CLIENT
    # ============================================================

    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "connexion/",
        views.connexion,
        name="connexion"
    ),

    path(
        "deconnexion/",
        views.deconnexion,
        name="deconnexion"
    ),

    path(
        "profil/",
        views.profil,
        name="profil"
    ),

    path(
        "consommation/",
        views.consommation,
        name="consommation"
    ),

    path(
        "compteur/<int:compteur_id>/",
        views.compteur_detail,
        name="compteur_detail"
    ),


    # ============================================================
    # ADMINISTRATEUR
    # ============================================================

    path(
        "admin-dashboard/",
        views.dashboard_admin,
        name="dashboard_admin"
    ),

    path(
        "admin-dashboard/clients/",
        views.clients_admin,
        name="clients_admin"
    ),




    path(
        "admin-dashboard/clients/nouveau/",
        views.client_create_admin,
        name="client_create_admin"
    ),

    path(
        "admin-dashboard/clients/<int:client_id>/modifier/",
        views.client_edit_admin,
        name="client_edit_admin"
    ),

    path(
        "admin-dashboard/clients/<int:client_id>/activer/",
        views.client_toggle_admin,
        name="client_toggle_admin"
    ),




    path(
        "admin-dashboard/compteurs/",
        views.compteurs_admin,
        name="compteurs_admin"
    ),

    # Recharge du solde d'un compteur
    path(
        "admin-dashboard/compteurs/<int:compteur_id>/recharger/",
        views.recharger_compteur_admin,
        name="recharger_compteur_admin"
    ),

    path(
        "admin-dashboard/historique/",
        views.historique_admin,
        name="historique_admin"
    ),


    # ============================================================
    # API ESP32 / PZEM
    # ============================================================

    path(
        "api/pzem/mesure/",
        views.api_pzem_mesure,
        name="api_pzem_mesure"
    ),

    path(
        "api/temps-reel/",
        views.api_temps_reel,
        name="api_temps_reel"
    ),

]