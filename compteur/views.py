
import json
import logging

from decimal import Decimal, InvalidOperation

from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# ============================================================
# IMPORT DES FORMULAIRES
# ============================================================

from .forms import (
    ClientCreationForm,
    ClientUpdateForm,
    CompteurAdminForm,
    CompteurUpdateForm,  # Formulaire de modification du compteur
)



from django.db.models import Sum

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import (
    Profil,
    Compteur,
    Mesure,
    HistoriqueCommande,
    MouvementSolde,
)

logger = logging.getLogger(__name__)


def _api_error(code, message, status, retryable=False):
    return JsonResponse(
        {
            "success": False,
            "message": message,
            "error": {
                "code": code,
                "message": message,
                "retryable": retryable,
            },
        },
        status=status,
    )


def _read_api_json(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, _api_error(
            "invalid_json",
            "Corps JSON invalide ou vide.",
            400,
        )

    if not isinstance(data, dict):
        return None, _api_error(
            "invalid_payload",
            "Le corps JSON doit être un objet.",
            400,
        )

    return data, None


def _required_device_id(data):
    device_id = data.get("device_id")
    if not isinstance(device_id, str) or not device_id.strip():
        return None, _api_error(
            "missing_device_id",
            "device_id doit être une chaîne non vide.",
            400,
        )

    device_id = device_id.strip()
    if len(device_id) > 50:
        return None, _api_error(
            "invalid_device_id",
            "device_id ne peut pas dépasser 50 caractères.",
            400,
        )

    return device_id, None


def _required_non_negative_decimal(data, field):
    value = data.get(field)
    if value is None or isinstance(value, bool):
        raise ValueError(f"Le champ {field} est obligatoire et doit être numérique.")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Le champ {field} doit être numérique.")

    if not number.is_finite() or number < 0:
        raise ValueError(f"Le champ {field} doit être un nombre fini positif ou nul.")

    return number




# ============================================================
# GESTION DU SOLDE ÉNERGIE
# ============================================================

@login_required
def recharger_compteur_admin(request, compteur_id):
    """
    Permet à un administrateur de recharger
    le solde kWh d'un compteur.

    Règle automatique :
    - Si le solde était à 0 avant la recharge
    - et devient supérieur à 0 après la recharge
    - et que le compteur est autorisé
    => le contacteur est automatiquement remis ON.
    """

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    compteur = get_object_or_404(
        Compteur,
        id=compteur_id
    )

    erreur = None

    # TRAITEMENT DU FORMULAIRE

    if request.method == "POST":

        quantite = request.POST.get("quantite")
        motif = request.POST.get(
            "motif",
            ""
        ).strip()

        if not motif:
            motif = "Recharge admin"

        solde_avant = compteur.solde

        try:

            ajouter_solde(
                compteur=compteur,
                quantite=quantite,
                motif=motif
            )

            # RECHARGEMENT DU COMPTEUR
            compteur.refresh_from_db()

            # RECONNEXION AUTOMATIQUE

            if (
                solde_avant <= 0
                and compteur.solde > 0
                and compteur.autorisation
                and not compteur.contacteur
            ):

                compteur.contacteur = True

                compteur.save(
                    update_fields=["contacteur"]
                )

                # HISTORIQUE DU CONTACTEUR
                HistoriqueCommande.objects.create(
                    compteur=compteur,
                    action="ON",
                    motif="Réactivation automatique après recharge"
                )

            # REDIRECTION

            return redirect(
                "compteur:compteurs_admin"
            )

        except ValueError as e:

            # Affiche l'erreur dans le formulaire.
            erreur = str(e)

    return render(
        request,
        "compteur/admin/recharger_compteur.html",
        {
            "compteur": compteur,
            "erreur": erreur,
        }
    )



def ajouter_solde(compteur, quantite, motif="Recharge"):
    """
    Ajoute une quantité de kWh au solde du compteur
    et enregistre l'opération dans l'historique.
    """

    try:

        quantite = Decimal(
            str(quantite)
        )

    except (InvalidOperation, ValueError, TypeError):

        raise ValueError(
            "La quantité de kWh est invalide."
        )


    if quantite <= 0:

        raise ValueError(
            "La quantité de recharge doit être supérieure à 0."
        )


    solde_avant = (
        compteur.solde
        or Decimal("0.000")
    )


    solde_apres = (
        solde_avant
        + quantite
    )


    compteur.solde = solde_apres


    compteur.save(
        update_fields=["solde"]
    )


    MouvementSolde.objects.create(

        compteur=compteur,

        type_operation="RECHARGE",

        quantite=quantite,

        motif=motif,

        solde_avant=solde_avant,

        solde_apres=solde_apres,
    )


    return compteur



# ============================================================
# PAGE VISITEUR
# ============================================================

def visiteur(request):
    """
    Page d'accueil publique accessible aux visiteurs.
    Les utilisateurs connectés sont redirigés vers
    leur espace correspondant.
    """
    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect(
                "compteur:dashboard_admin"
            )

        # Client
        return redirect(
            "compteur:dashboard"
        )

    # Visiteur non connecté
    return render(
        request,
        "compteur/visiteur.html"
    )



# ============================================================
# CONNEXION
# ============================================================

def connexion(request):

    if request.user.is_authenticated:

        if request.user.is_staff:

            return redirect(
                "compteur:dashboard_admin"
            )

        return redirect(
            "compteur:dashboard"
        )


    erreur = None


    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )


        utilisateur = authenticate(

            request,

            username=username,

            password=password
        )


        if utilisateur is not None:

            login(
                request,
                utilisateur
            )


            if utilisateur.is_staff:

                return redirect(
                    "compteur:dashboard_admin"
                )


            return redirect(
                "compteur:dashboard"
            )


        erreur = (
            "Nom d'utilisateur ou mot de passe incorrect."
        )


    return render(

        request,

        "compteur/connexion.html",

        {
            "erreur": erreur
        }
    )


# ============================================================
# DECONNEXION
# ============================================================

@login_required
def deconnexion(request):

    logout(request)


    return redirect(
        "compteur:connexion"
    )


# ============================================================
# DASHBOARD CLIENT
# ============================================================

@login_required
def dashboard(request):

    if request.user.is_staff:

        return redirect(
            "compteur:dashboard_admin"
        )


    compteurs = (
        Compteur.objects
        .filter(
            utilisateur=request.user
        )
        .order_by("nom")
    )


    nombre_compteurs = (
        compteurs.count()
    )


    compteurs_connectes = (
        compteurs
        .filter(
            esp32_connecte=True
        )
        .count()
    )


    compteurs_autorises = (
        compteurs
        .filter(
            autorisation=True
        )
        .count()
    )


    solde_total = (
        compteurs.aggregate(
            total=Sum("solde")
        )["total"]
        or 0
    )


    consommation_totale = (
        compteurs.aggregate(
            total=Sum("consommation_totale")
        )["total"]
        or 0
    )


    compteurs_data = []


    for compteur in compteurs:

        derniere_mesure = (
            Mesure.objects
            .filter(
                compteur=compteur
            )
            .order_by("-date_mesure")
            .first()
        )


        compteurs_data.append({

            "compteur": compteur,

            "mesure": derniere_mesure,

        })


    derniere_mesure = (
        Mesure.objects
        .filter(
            compteur__utilisateur=request.user
        )
        .order_by("-date_mesure")
        .first()
    )


    profil = getattr(

        request.user,

        "profil",

        None
    )


    context = {

        "profil": profil,

        "compteurs": compteurs_data,

        "nombre_compteurs":
            nombre_compteurs,

        "compteurs_connectes":
            compteurs_connectes,

        "compteurs_autorises":
            compteurs_autorises,

        "solde_total":
            solde_total,

        "consommation_totale":
            consommation_totale,

        "derniere_mesure":
            derniere_mesure,

    }


    return render(

        request,

        "compteur/client/dashboard.html",

        context
    )


# ============================================================
# DETAIL COMPTEUR
# ============================================================

@login_required
def compteur_detail(
    request,
    compteur_id
):

    if request.user.is_staff:

        compteur = get_object_or_404(

            Compteur,

            id=compteur_id
        )

    else:

        compteur = get_object_or_404(

            Compteur,

            id=compteur_id,

            utilisateur=request.user
        )


    mesures = (
        Mesure.objects
        .filter(
            compteur=compteur
        )
        .order_by("-date_mesure")[:10]
    )


    commandes = (
        HistoriqueCommande.objects
        .filter(
            compteur=compteur
        )
        .order_by("-date_action")[:10]
    )


    derniere_mesure = (
        mesures.first()
    )


    context = {

        "compteur":
            compteur,

        "mesures":
            mesures,

        "commandes":
            commandes,

        "derniere_mesure":
            derniere_mesure,

    }


    return render(

        request,

        "compteur/client/compteur_detail.html",

        context
    )


# ============================================================
# CONSOMMATION CLIENT
# ============================================================

@login_required
def consommation(request):

    if request.user.is_staff:

        return redirect(
            "compteur:dashboard_admin"
        )


    compteurs = Compteur.objects.filter(

        utilisateur=request.user
    )


    donnees = []


    for compteur in compteurs:

        mesures = list(

            Mesure.objects
            .filter(
                compteur=compteur
            )
            .order_by("-date_mesure")[:24]
        )


        mesures.reverse()


        labels = [

            mesure.date_mesure.strftime(
                "%H:%M"
            )

            for mesure in mesures

        ]


        energies = [

            float(
                mesure.energie
            )

            for mesure in mesures

        ]


        puissances = [

            float(
                mesure.puissance
            )

            for mesure in mesures

        ]


        donnees.append({

            "compteur":
                compteur,

            "labels":
                labels,

            "energies":
                energies,

            "puissances":
                puissances,

        })


    return render(

        request,

        "compteur/client/consommation.html",

        {
            "donnees": donnees
        }
    )


# ============================================================
# PROFIL CLIENT
# ============================================================

@login_required
def profil(request):

    if request.user.is_staff:

        return redirect(
            "compteur:dashboard_admin"
        )


    profil = getattr(

        request.user,

        "profil",

        None
    )


    if request.method == "POST":

        if profil:

            profil.nom = request.POST.get(

                "nom",

                profil.nom
            )


            profil.prenom = request.POST.get(

                "prenom",

                profil.prenom
            )


            profil.telephone = request.POST.get(

                "telephone",

                profil.telephone
            )


            profil.adresse = request.POST.get(

                "adresse",

                profil.adresse
            )


            profil.ville = request.POST.get(

                "ville",

                profil.ville
            )


            profil.fokontany = request.POST.get(

                "fokontany",

                profil.fokontany
            )


            profil.profession = request.POST.get(

                "profession",

                profil.profession
            )


            profil.save()


        request.user.email = request.POST.get(

            "email",

            request.user.email
        )


        request.user.save()


    return render(

        request,

        "compteur/client/profil.html",

        {
            "profil": profil
        }
    )


# ============================================================
# DASHBOARD ADMIN
# ============================================================

@login_required
def dashboard_admin(request):

    if not request.user.is_staff:

        return redirect(
            "compteur:dashboard"
        )


    nombre_clients = (
        Profil.objects.count()
    )


    nombre_compteurs = (
        Compteur.objects.count()
    )


    compteurs_connectes = (
        Compteur.objects
        .filter(
            esp32_connecte=True
        )
        .count()
    )


    compteurs_coupes = (
        Compteur.objects
        .filter(
            contacteur=False
        )
        .count()
    )


    solde_total = (
        Compteur.objects.aggregate(
            total=Sum("solde")
        )["total"]
        or 0
    )


    consommation_totale = (
        Compteur.objects.aggregate(
            total=Sum("consommation_totale")
        )["total"]
        or 0
    )


    derniers_compteurs = (

        Compteur.objects

        .select_related(
            "utilisateur"
        )

        .order_by(
            "-date_creation"
        )[:10]

    )


    dernieres_commandes = (

        HistoriqueCommande.objects

        .select_related(
            "compteur"
        )

        .order_by(
            "-date_action"
        )[:10]

    )


    context = {

        "nombre_clients":
            nombre_clients,

        "nombre_compteurs":
            nombre_compteurs,

        "compteurs_connectes":
            compteurs_connectes,

        "compteurs_coupes":
            compteurs_coupes,

        "solde_total":
            solde_total,

        "consommation_totale":
            consommation_totale,

        "derniers_compteurs":
            derniers_compteurs,

        "dernieres_commandes":
            dernieres_commandes,

    }


    return render(

        request,

        "compteur/admin/dashboard.html",

        context
    )


# ============================================================
# ADMIN - CLIENTS
# ============================================================

@login_required
def clients_admin(request):

    if not request.user.is_staff:

        return redirect(
            "compteur:dashboard"
        )


    clients = (

        Profil.objects

        .select_related(
            "utilisateur"
        )

        .order_by(
            "-date_inscription"
        )

    )


    return render(

        request,

        "compteur/admin/clients.html",

        {
            "clients": clients
        }
    )



# ============================================================
# CRÉER UN CLIENT
# ============================================================

@login_required
def client_create_admin(request):

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    if request.method == "POST":

        form = ClientCreationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect(
                "compteur:clients_admin"
            )

    else:

        form = ClientCreationForm()

    return render(
        request,
        "compteur/admin/client_form.html",
        {
            "form": form,
            "mode": "creation",
            "titre": "Nouveau client",
        }
    )


# ============================================================
# MODIFIER UN CLIENT
# ============================================================

@login_required
def client_edit_admin(request, client_id):

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    profil = get_object_or_404(
        Profil.objects.select_related("utilisateur"),
        id=client_id
    )

    if request.method == "POST":

        form = ClientUpdateForm(
            request.POST,
            request.FILES,
            instance=profil
        )

        if form.is_valid():

            form.save()

            return redirect(
                "compteur:clients_admin"
            )

    else:

        form = ClientUpdateForm(
            instance=profil
        )

    return render(
        request,
        "compteur/admin/client_form.html",
        {
            "form": form,
            "mode": "modification",
            "titre": "Modifier le client",
            "client": profil,
        }
    )


# ============================================================
# ACTIVER / DÉSACTIVER UN CLIENT
# ============================================================

@login_required
def client_toggle_admin(request, client_id):

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    profil = get_object_or_404(
        Profil,
        id=client_id
    )

    profil.actif = not profil.actif
    profil.save(update_fields=["actif"])

    return redirect(
        "compteur:clients_admin"
    )



# ============================================================
# COMPTEURS D'UN CLIENT
# ============================================================

@login_required
def client_compteurs_admin(request, client_id):

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    profil = get_object_or_404(
        Profil.objects.select_related("utilisateur"),
        id=client_id
    )

    compteurs = (
        Compteur.objects
        .filter(utilisateur=profil.utilisateur)
        .order_by("nom")
    )

    # STATISTIQUES DU CLIENT

    statistiques = compteurs.aggregate(
        solde_total=Sum("solde"),
        consommation_totale=Sum("consommation_totale"),
    )

    solde_total = statistiques["solde_total"] or 0
    consommation_totale = statistiques["consommation_totale"] or 0

    compteurs_connectes = compteurs.filter(
        esp32_connecte=True
    ).count()

    compteurs_coupes = compteurs.filter(
        contacteur=False
    ).count()

    return render(
        request,
        "compteur/admin/client_compteurs.html",
        {
            "client": profil,
            "compteurs": compteurs,

            "solde_total": solde_total,
            "consommation_totale": consommation_totale,

            "compteurs_connectes": compteurs_connectes,
            "compteurs_coupes": compteurs_coupes,
        }
    )


# ============================================================
# API - COMPTEURS D'UN CLIENT
# ============================================================

@login_required
def api_client_compteurs_admin(request, client_id):

    if not request.user.is_staff:
        return JsonResponse(
            {
                "success": False,
                "message": "Accès administrateur requis."
            },
            status=403
        )

    profil = get_object_or_404(
        Profil.objects.select_related("utilisateur"),
        id=client_id
    )

    compteurs = (
        Compteur.objects
        .filter(utilisateur=profil.utilisateur)
        .order_by("nom")
    )

    donnees = []

    for compteur in compteurs:

        derniere_mesure = (
            compteur.mesures
            .order_by("-date_mesure")
            .first()
        )

        donnees.append({
            "id": compteur.id,
            "device_id": compteur.device_id,
            "nom": compteur.nom,

            "solde": float(compteur.solde or 0),
            "consommation_totale": float(
                compteur.consommation_totale or 0
            ),

            "autorisation": compteur.autorisation,
            "contacteur": compteur.contacteur,
            "esp32_connecte": compteur.esp32_connecte,

            "derniere_connexion": (
                compteur.derniere_connexion.isoformat()
                if compteur.derniere_connexion
                else None
            ),

            "mesure": (
                {
                    "tension": float(
                        derniere_mesure.tension or 0
                    ),
                    "courant": float(
                        derniere_mesure.courant or 0
                    ),
                    "puissance": float(
                        derniere_mesure.puissance or 0
                    ),
                    "energie": float(
                        derniere_mesure.energie or 0
                    ),
                    "date_mesure": (
                        derniere_mesure.date_mesure.isoformat()
                    ),
                }
                if derniere_mesure
                else None
            ),
        })

    solde_total = sum(
        compteur["solde"]
        for compteur in donnees
    )

    consommation_totale = sum(
        compteur["consommation_totale"]
        for compteur in donnees
    )

    compteurs_connectes = sum(
        1
        for compteur in donnees
        if compteur["esp32_connecte"]
    )

    compteurs_coupes = sum(
        1
        for compteur in donnees
        if not compteur["contacteur"]
    )

    return JsonResponse({
        "success": True,

        "client": {
            "id": profil.id,
            "nom": profil.nom,
            "prenom": profil.prenom,
        },

        "compteurs": donnees,

        "statistiques": {
            "nombre_compteurs": len(donnees),
            "solde_total": solde_total,
            "consommation_totale": consommation_totale,
            "compteurs_connectes": compteurs_connectes,
            "compteurs_coupes": compteurs_coupes,
        }
    })

# ============================================================
# client compteur ADMIN
# ============================================================

@login_required
def client_compteur_create_admin(request, client_id):

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    profil = get_object_or_404(
        Profil.objects.select_related("utilisateur"),
        id=client_id
    )

    if request.method == "POST":

        form = CompteurAdminForm(
            request.POST
        )

        if form.is_valid():

            compteur = form.save(
                commit=False
            )

            # Le compteur appartient au client sélectionné
            compteur.utilisateur = (
                profil.utilisateur
            )

            compteur.save()

            return redirect(
                "compteur:client_compteurs_admin",
                client_id=client_id
            )

    else:

        form = CompteurAdminForm()

    return render(
        request,
        "compteur/admin/compteur_form.html",
        {
            "form": form,
            "client": profil,
            "mode": "creation",
            "titre": "Nouveau compteur",
        }
    )



# ============================================================
# MODIFIER UN COMPTEUR - ADMIN
# ============================================================

@login_required
def client_compteur_edit_admin(request, client_id, compteur_id):

    # Vérifie que l'utilisateur connecté est administrateur

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    # Récupère le client sélectionné

    profil = get_object_or_404(
        Profil.objects.select_related("utilisateur"),
        id=client_id
    )


    # Récupère le compteur
  
    compteur = get_object_or_404(
        Compteur,
        id=compteur_id,
        utilisateur=profil.utilisateur
    )


    # TRAITEMENT DU FORMULAIRE

    if request.method == "POST":

        form = CompteurUpdateForm(
            request.POST,
            instance=compteur
        )


        # Vérifie que toutes les données sont valides
        if form.is_valid():

            # Enregistre les modifications
            form.save()

            return redirect(
                "compteur:client_compteurs_admin",
                client_id=client_id
            )


    # AFFICHAGE INITIAL DU FORMULAIRE

    else:

        form = CompteurUpdateForm(
            instance=compteur
        )

    # AFFICHAGE DE LA PAGE

    return render(
        request,
        "compteur/admin/compteur_form.html",
        {
            # Formulaire de modification
            "form": form,

            # Client auquel appartient le compteur
            "client": profil,

            # Compteur actuellement modifié
            "compteur": compteur,

            # Indique que nous sommes en modification
            "mode": "modification",

            # Titre affiché dans la page
            "titre": "Modifier le compteur",
        }
    )



# ============================================================
# CHANGER L'ÉTAT DU CONTACTEUR - ADMIN
# ============================================================

@login_required
def client_compteur_toggle_contacteur_admin(
    request,
    client_id,
    compteur_id
):

    # Vérifie que l'utilisateur connecté est administrateur

    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    # Récupère le client concerné

    profil = get_object_or_404(
        Profil.objects.select_related("utilisateur"),
        id=client_id
    )

    # Récupère le compteur.

    compteur = get_object_or_404(
        Compteur,
        id=compteur_id,
        utilisateur=profil.utilisateur
    )

    # Inverse l'état actuel du contacteur

    compteur.contacteur = not compteur.contacteur

    # Enregistre le nouvel état dans la base de données

    compteur.save(
        update_fields=["contacteur"]
    )

    # ENREGISTREMENT DANS L'HISTORIQUE

    if compteur.contacteur:

        # Le nouveau statut est ON
        action = "ON"

        # Motif enregistré dans l'historique
        motif = "Activation manuelle par l'administrateur"

    else:

        # Le nouveau statut est OFF
        action = "OFF"

        # Motif enregistré dans l'historique
        motif = "Coupure manuelle par l'administrateur"

    # Création de l'entrée dans l'historique

    HistoriqueCommande.objects.create(
        compteur=compteur,
        action=action,
        motif=motif
    )
    # Retour à la page des compteurs du client

    return redirect(
        "compteur:client_compteurs_admin",
        client_id=client_id
    )




# ============================================================
# ADMIN - COMPTEURS
# ============================================================

@login_required
def compteurs_admin(request):

    if not request.user.is_staff:

        return redirect(
            "compteur:dashboard"
        )


    compteurs = (

        Compteur.objects

        .select_related(
            "utilisateur"
        )

        .order_by(
            "-date_creation"
        )

    )


    return render(

        request,

        "compteur/admin/compteurs.html",

        {
            "compteurs": compteurs
        }
    )


# ============================================================
# HISTORIQUE DES COMMANDES - ADMIN
# ============================================================
@login_required
def historique_admin(request):

    # Vérifie que l'utilisateur connecté est administrateur

    if not request.user.is_staff:
        return redirect("compteur:dashboard")
    
    # Récupère les commandes les plus récentes en premier.

    historique = (
        HistoriqueCommande.objects
        .select_related(
            "compteur",
            "compteur__utilisateur",
            "compteur__utilisateur__profil",
        )
        .order_by("-date_action")
    )


    # Envoie les données au template.

    return render(
        request,
        "compteur/admin/historique.html",
        {
            "historique": historique,
        }
    )


# ============================================================
# API PZEM - RECEPTION DES MESURES ESP32
# ============================================================

@csrf_exempt
def api_pzem_mesure(request):
    if request.method != "POST":
        return _api_error(
            "method_not_allowed",
            "Cette route accepte uniquement la méthode POST.",
            405,
        )

    data, error_response = _read_api_json(request)
    if error_response:
        return error_response

    device_id, error_response = _required_device_id(data)
    if error_response:
        return error_response

    try:
        measurements = {
            field: _required_non_negative_decimal(data, field)
            for field in ("tension", "courant", "puissance", "energie")
        }
    except ValueError as error:
        return _api_error("invalid_measurement", str(error), 400)

    try:
        with transaction.atomic():
            compteur = (
                Compteur.objects.select_for_update()
                .filter(device_id=device_id)
                .first()
            )
            if compteur is None:
                return _api_error(
                    "counter_not_found",
                    f"Aucun compteur ne correspond à device_id « {device_id} ».",
                    404,
                )

            derniere_mesure = (
                Mesure.objects.filter(compteur=compteur)
                .order_by("-date_mesure")
                .first()
            )
            energie_actuelle = measurements["energie"]
            consommation = Decimal("0.000")
            if derniere_mesure:
                consommation = max(
                    energie_actuelle - derniere_mesure.energie,
                    Decimal("0.000"),
                )

            mesure = Mesure.objects.create(
                compteur=compteur,
                tension=measurements["tension"],
                courant=measurements["courant"],
                puissance=measurements["puissance"],
                energie=energie_actuelle,
            )

            compteur.consommation_totale += consommation
            if consommation > 0:
                solde_avant = compteur.solde
                compteur.solde = max(
                    solde_avant - consommation,
                    Decimal("0.000"),
                )
                MouvementSolde.objects.create(
                    compteur=compteur,
                    type_operation="CONSOMMATION",
                    quantite=consommation,
                    motif="Consommation PZEM",
                    solde_avant=solde_avant,
                    solde_apres=compteur.solde,
                )

                if compteur.solde <= 0 and compteur.contacteur:
                    compteur.contacteur = False
                    HistoriqueCommande.objects.create(
                        compteur=compteur,
                        action="OFF",
                        motif="Coupure automatique : solde épuisé",
                    )

            if not compteur.autorisation and compteur.contacteur:
                compteur.contacteur = False
                HistoriqueCommande.objects.create(
                    compteur=compteur,
                    action="OFF",
                    motif="Coupure automatique : compteur non autorisé",
                )

            compteur.esp32_connecte = True
            compteur.derniere_connexion = timezone.now()
            compteur.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Mesure PZEM enregistrée.",
                "device_id": compteur.device_id,
                "mesure_id": mesure.id,
                "energie": float(energie_actuelle),
                "consommation": float(consommation),
                "consommation_totale": float(compteur.consommation_totale),
                "solde": float(compteur.solde),
                "autorisation": compteur.autorisation,
                "contacteur": compteur.contacteur,
            }
        )
    except DatabaseError:
        logger.exception("Erreur de base de données pendant la réception PZEM.")
        return _api_error(
            "database_error",
            "La mesure n'a pas pu être enregistrée. Réessayez.",
            503,
            retryable=True,
        )
    except Exception:
        logger.exception("Erreur inattendue pendant la réception PZEM.")
        return _api_error(
            "internal_error",
            "Erreur interne lors du traitement de la mesure.",
            500,
            retryable=True,
        )


# ============================================================
# API ESP32 - ETAT DU COMPTEUR
# ============================================================

@csrf_exempt
def api_esp32_etat(request, device_id):
    if request.method != "GET":
        return _api_error(
            "method_not_allowed",
            "Cette route accepte uniquement la méthode GET.",
            405,
        )

    compteur = Compteur.objects.filter(device_id=device_id).first()
    if compteur is None:
        return _api_error(
            "counter_not_found",
            f"Aucun compteur ne correspond à device_id « {device_id} ».",
            404,
        )

    return JsonResponse(
        {
            "success": True,
            "message": "État du compteur récupéré.",
            "device_id": compteur.device_id,
            "solde": float(compteur.solde or 0),
            "autorisation": compteur.autorisation,
            "contacteur": compteur.contacteur and compteur.autorisation,
            "esp32_connecte": compteur.esp32_connecte,
            "derniere_connexion": (
                compteur.derniere_connexion.isoformat()
                if compteur.derniere_connexion
                else None
            ),
        }
    )


# ============================================================
# API ESP32 - RETOUR ETAT REEL DU RELAIS
# ============================================================

@csrf_exempt
def api_esp32_heartbeat(request):
    if request.method != "POST":
        return _api_error(
            "method_not_allowed",
            "Cette route accepte uniquement la méthode POST.",
            405,
        )

    data, error_response = _read_api_json(request)
    if error_response:
        return error_response

    device_id, error_response = _required_device_id(data)
    if error_response:
        return error_response

    relais_on = data.get("relais_on")
    if not isinstance(relais_on, bool):
        return _api_error(
            "invalid_relay_state",
            "relais_on doit être un booléen JSON (true ou false).",
            400,
        )

    try:
        with transaction.atomic():
            compteur = (
                Compteur.objects.select_for_update()
                .filter(device_id=device_id)
                .first()
            )
            if compteur is None:
                return _api_error(
                    "counter_not_found",
                    f"Aucun compteur ne correspond à device_id « {device_id} ».",
                    404,
                )

            compteur.contacteur = relais_on and compteur.autorisation
            compteur.esp32_connecte = True
            compteur.derniere_connexion = timezone.now()
            compteur.save(
                update_fields=[
                    "contacteur",
                    "esp32_connecte",
                    "derniere_connexion",
                ]
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Heartbeat ESP32 reçu.",
                "device_id": compteur.device_id,
                "relais_on": compteur.contacteur,
                "autorisation": compteur.autorisation,
                "solde": float(compteur.solde or 0),
                "esp32_connecte": compteur.esp32_connecte,
                "derniere_connexion": compteur.derniere_connexion.isoformat(),
            }
        )
    except DatabaseError:
        logger.exception("Erreur de base de données pendant le heartbeat ESP32.")
        return _api_error(
            "database_error",
            "Le heartbeat n'a pas pu être enregistré. Réessayez.",
            503,
            retryable=True,
        )
    except Exception:
        logger.exception("Erreur inattendue pendant le heartbeat ESP32.")
        return _api_error(
            "internal_error",
            "Erreur interne lors du traitement du heartbeat.",
            500,
            retryable=True,
        )



# ============================================================
# API TEMPS REEL
# ============================================================

@login_required
def api_temps_reel(request):

    # COMPTEURS

    if request.user.is_staff:

        compteurs = (
            Compteur.objects
            .select_related("utilisateur")
            .all()
        )

    else:

        compteurs = (
            Compteur.objects
            .filter(
                utilisateur=request.user
            )
            .select_related("utilisateur")
        )


    resultats = []

    # TRAITEMENT DES COMPTEURS

    for compteur in compteurs:

        mesures = list(

            Mesure.objects
            .filter(
                compteur=compteur
            )
            .order_by(
                "-date_mesure"
            )[:24]

        )


        # DERNIÈRE MESURE

        derniere_mesure = (

            mesures[0]

            if mesures

            else None

        )

        # ORDRE CHRONOLOGIQUE

        mesures.reverse()


        historique = []

        # HISTORIQUE

        for mesure in mesures:

            historique.append({

                "tension":
                    float(mesure.tension),

                "courant":
                    float(mesure.courant),

                "puissance":
                    float(mesure.puissance),

                "energie":
                    float(mesure.energie),

                "date_mesure":
                    mesure.date_mesure.isoformat(),

                "heure":
                    mesure.date_mesure.strftime(
                        "%H:%M:%S"
                    ),

            })

        # COMPTEUR

        resultats.append({

            "id":
                compteur.id,

            "device_id":
                compteur.device_id,

            "nom":
                compteur.nom,

            "utilisateur_id":
                compteur.utilisateur_id,

            "solde":
                float(
                    compteur.solde or 0
                ),

            "consommation_totale":
                float(
                    compteur.consommation_totale or 0
                ),

            "autorisation":
                compteur.autorisation,

            "contacteur":
                compteur.contacteur,

            "esp32_connecte":
                compteur.esp32_connecte,

            "derniere_connexion": (

                compteur.derniere_connexion.isoformat()

                if compteur.derniere_connexion

                else None

            ),

            # DERNIÈRE MESURE

            "mesure": (

                {

                    "tension":
                        float(
                            derniere_mesure.tension
                        ),

                    "courant":
                        float(
                            derniere_mesure.courant
                        ),

                    "puissance":
                        float(
                            derniere_mesure.puissance
                        ),

                    "energie":
                        float(
                            derniere_mesure.energie
                        ),

                    "date_mesure":
                        derniere_mesure
                        .date_mesure
                        .isoformat(),

                }

                if derniere_mesure

                else None

            ),

            # HISTORIQUE PZEM

            "mesures":
                historique,

        })

    # STATISTIQUES ADMINISTRATEUR

    statistiques_admin = {

        "nombre_clients":
            Profil.objects.count(),

        "nombre_compteurs":
            Compteur.objects.count(),

        "compteurs_connectes":
            Compteur.objects.filter(
                esp32_connecte=True
            ).count(),

        "compteurs_coupes":
            Compteur.objects.filter(
                contacteur=False
            ).count(),

        "solde_total":
            float(
                Compteur.objects.aggregate(
                    total=Sum("solde")
                )["total"] or 0
            ),

        "consommation_totale":
            float(
                Compteur.objects.aggregate(
                    total=Sum("consommation_totale")
                )["total"] or 0
            ),

    }


    return JsonResponse({

        "success":
            True,

        "compteurs":
            resultats,

        "statistiques_admin":
            statistiques_admin,

    })



# ============================================================
# API ADMIN - LISTE DES CLIENTS
# ============================================================

@login_required
def api_admin_clients(request):

    # SÉCURITÉ

    if not request.user.is_staff:

        return JsonResponse(
            {
                "success": False,
                "message": "Accès administrateur requis."
            },
            status=403
        )

    # MÉTHODE HTTP

    if request.method != "GET":

        return JsonResponse(
            {
                "success": False,
                "message": "Méthode GET uniquement."
            },
            status=405
        )

    # RÉCUPÉRATION DES CLIENTS

    clients = (
        Profil.objects
        .select_related("utilisateur")
        .prefetch_related("utilisateur__compteurs")
        .order_by("-date_inscription")
    )

    resultats = []

    # CONSTRUCTION DES DONNÉES JSON

    for client in clients:

        compteurs = list(
            client.utilisateur.compteurs.all()
        )

        photo = None

        if client.photo_user:

            photo = client.photo_user.url

        email = client.utilisateur.email or ""

        nom_complet = (
            f"{client.prenom} {client.nom}"
        ).strip()

        resultats.append({

            "id":
                client.id,

            "nom":
                client.nom,

            "prenom":
                client.prenom,

            "nom_complet":
                nom_complet,

            "username":
                client.utilisateur.username,

            "email":
                email,

            "telephone":
                client.telephone or "",

            "adresse":
                client.adresse or "",

            "ville":
                client.ville or "",

            "fokontany":
                client.fokontany or "",

            "actif":
                client.actif,

            "photo":
                photo,

            "nombre_compteurs":
                len(compteurs),

            "date_inscription": (

                client.date_inscription.isoformat()

                if client.date_inscription

                else None

            ),

        })

    nombre_clients = len(resultats)

    clients_actifs = sum(
        1
        for client in resultats
        if client["actif"]
    )

    clients_inactifs = (
        nombre_clients
        - clients_actifs
    )


    return JsonResponse({

        "success":
            True,

        "clients":
            resultats,

        "statistiques": {

            "nombre_clients":
                nombre_clients,

            "clients_actifs":
                clients_actifs,

            "clients_inactifs":
                clients_inactifs,

        }

    })


# ============================================================
# API ADMIN - LISTE DES COMPTEURS
# ============================================================

@login_required
def api_admin_compteurs(request):

    if not request.user.is_staff:

        return JsonResponse(
            {
                "success": False,
                "message": "Accès administrateur requis."
            },
            status=403
        )


    if request.method != "GET":

        return JsonResponse(
            {
                "success": False,
                "message": "Méthode GET uniquement."
            },
            status=405
        )

    # RÉCUPÉRATION DES COMPTEURS

    compteurs = (
        Compteur.objects
        .select_related("utilisateur")
        .prefetch_related("mesures")
        .order_by("-date_creation")
    )

    resultats = []

    # CONSTRUCTION DES DONNÉES

    for compteur in compteurs:


        profil = None

        try:
            profil = compteur.utilisateur.profil
        except Profil.DoesNotExist:
            profil = None


        if profil:

            client_nom = (
                f"{profil.prenom} {profil.nom}"
            ).strip()

        else:

            client_nom = (
                compteur.utilisateur.get_full_name()
                or compteur.utilisateur.username
            )

        # DERNIÈRE MESURE

        derniere_mesure = (
            compteur.mesures
            .order_by("-date_mesure")
            .first()
        )

        mesure_data = None

        if derniere_mesure:

            mesure_data = {

                "id":
                    derniere_mesure.id,

                "tension":
                    float(derniere_mesure.tension),

                "courant":
                    float(derniere_mesure.courant),

                "puissance":
                    float(derniere_mesure.puissance),

                "energie":
                    float(derniere_mesure.energie),

                "date_mesure":
                    (
                        derniere_mesure.date_mesure.isoformat()
                        if derniere_mesure.date_mesure
                        else None
                    ),
            }

        # DERNIÈRES MESURES POUR GRAPHIQUES

        mesures = list(
            compteur.mesures
            .order_by("-date_mesure")[:24]
        )

        mesures.reverse()

        historique_mesures = []

        for mesure in mesures:

            historique_mesures.append({

                "tension":
                    float(mesure.tension),

                "courant":
                    float(mesure.courant),

                "puissance":
                    float(mesure.puissance),

                "energie":
                    float(mesure.energie),

                "date_mesure":
                    (
                        mesure.date_mesure.isoformat()
                        if mesure.date_mesure
                        else None
                    ),

            })

        # DERNIÈRE CONNEXION ESP32

        derniere_connexion = None

        if compteur.derniere_connexion:

            derniere_connexion = (
                compteur.derniere_connexion.isoformat()
            )

        # DONNÉES DU COMPTEUR

        resultats.append({

            "id":
                compteur.id,

            "device_id":
                compteur.device_id,

            "nom":
                compteur.nom,

            "utilisateur_id":
                compteur.utilisateur.id,

            "username":
                compteur.utilisateur.username,

            "client_nom":
                client_nom,

            "email":
                compteur.utilisateur.email or "",

            "solde":
                float(compteur.solde),

            "consommation_totale":
                float(compteur.consommation_totale),

            "autorisation":
                compteur.autorisation,

            "contacteur":
                compteur.contacteur,

            "esp32_connecte":
                compteur.esp32_connecte,

            "derniere_connexion":
                derniere_connexion,

            "derniere_mesure":
                mesure_data,

            "mesures":
                historique_mesures,

            "date_creation":
                (
                    compteur.date_creation.isoformat()
                    if compteur.date_creation
                    else None
                ),

        })

    # STATISTIQUES

    nombre_compteurs = len(resultats)

    compteurs_connectes = sum(
        1
        for compteur in resultats
        if compteur["esp32_connecte"]
    )

    compteurs_coupes = sum(
        1
        for compteur in resultats
        if not compteur["contacteur"]
    )

    compteurs_non_autorises = sum(
        1
        for compteur in resultats
        if not compteur["autorisation"]
    )

    solde_total = sum(
        compteur["solde"]
        for compteur in resultats
    )

    consommation_totale = sum(
        compteur["consommation_totale"]
        for compteur in resultats
    )

    return JsonResponse({

        "success":
            True,

        "compteurs":
            resultats,

        "statistiques": {

            "nombre_compteurs":
                nombre_compteurs,

            "compteurs_connectes":
                compteurs_connectes,

            "compteurs_coupes":
                compteurs_coupes,

            "compteurs_non_autorises":
                compteurs_non_autorises,

            "solde_total":
                round(solde_total, 3),

            "consommation_totale":
                round(consommation_totale, 3),

        }

    })
