from django.contrib import admin

from .models import (
    Profil,
    Compteur,
    Mesure,
    HistoriqueCommande,
    MouvementSolde,
)


# ============================================================
# PROFIL
# ============================================================

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):

    list_display = (
        "prenom",
        "nom",
        "utilisateur",
        "telephone",
        "ville",
        "cin",
        "actif",
    )

    search_fields = (
        "prenom",
        "nom",
        "telephone",
        "cin",
        "utilisateur__username",
        "utilisateur__email",
    )

    list_filter = (
        "actif",
        "cin_verifiee",
        "telephone_verifie",
        "email_verifie",
    )


# ============================================================
# COMPTEUR
# ============================================================

@admin.register(Compteur)
class CompteurAdmin(admin.ModelAdmin):

    list_display = (
        "device_id",
        "nom",
        "utilisateur",
        "solde",
        "consommation_totale",
        "autorisation",
        "contacteur",
        "esp32_connecte",
        "derniere_connexion",
    )

    search_fields = (
        "device_id",
        "nom",
        "utilisateur__username",
    )

    list_filter = (
        "autorisation",
        "contacteur",
        "esp32_connecte",
    )

    ordering = (
        "-date_creation",
    )


# ============================================================
# MESURE PZEM
# ============================================================

@admin.register(Mesure)
class MesureAdmin(admin.ModelAdmin):

    list_display = (
        "compteur",
        "tension",
        "courant",
        "puissance",
        "energie",
        "date_mesure",
    )

    search_fields = (
        "compteur__device_id",
        "compteur__nom",
    )

    list_filter = (
        "compteur",
        "date_mesure",
    )

    ordering = (
        "-date_mesure",
    )


# ============================================================
# HISTORIQUE DES COMMANDES
# ============================================================

@admin.register(HistoriqueCommande)
class HistoriqueCommandeAdmin(admin.ModelAdmin):

    list_display = (
        "compteur",
        "action",
        "motif",
        "date_action",
    )

    search_fields = (
        "compteur__device_id",
        "compteur__nom",
        "motif",
    )

    list_filter = (
        "action",
        "date_action",
    )

    ordering = (
        "-date_action",
    )


# ============================================================
# MOUVEMENT DU SOLDE
# ============================================================

@admin.register(MouvementSolde)
class MouvementSoldeAdmin(admin.ModelAdmin):

    list_display = (
        "compteur",
        "type_operation",
        "quantite",
        "solde_avant",
        "solde_apres",
        "motif",
        "date_operation",
    )

    search_fields = (
        "compteur__device_id",
        "compteur__nom",
        "motif",
    )

    list_filter = (
        "type_operation",
        "date_operation",
    )

    ordering = (
        "-date_operation",
    )

    # Ces valeurs sont calculées automatiquement
    # et ne doivent pas être modifiées manuellement.
    readonly_fields = (
        "solde_avant",
        "solde_apres",
        "date_operation",
    )