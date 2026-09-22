
import json

from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import ClientCreationForm, ClientUpdateForm

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


# ============================================================
# GESTION DU SOLDE ÉNERGIE
# ============================================================


@login_required
def recharger_compteur_admin(request, compteur_id):
    """
    Permet à un administrateur de recharger
    le solde kWh d'un compteur.
    """

    # Sécurité : seul le personnel admin peut accéder
    if not request.user.is_staff:
        return redirect("compteur:dashboard")

    compteur = get_object_or_404(
        Compteur,
        id=compteur_id
    )

    erreur = None

    if request.method == "POST":

        quantite = request.POST.get("quantite")

        motif = request.POST.get(
            "motif",
            ""
        ).strip()

        if not motif:
            motif = "Recharge admin"

        try:
            ajouter_solde(
                compteur=compteur,
                quantite=quantite,
                motif=motif
            )

            return redirect(
                "compteur:compteurs_admin"
            )

        except ValueError as e:
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
        .order_by("-date_mesure")[:50]
    )


    commandes = (
        HistoriqueCommande.objects
        .filter(
            compteur=compteur
        )
        .order_by("-date_action")[:20]
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
# ADMIN - HISTORIQUE COMMANDES
# ============================================================

@login_required
def historique_admin(request):

    if not request.user.is_staff:

        return redirect(
            "compteur:dashboard"
        )


    historique = (

        HistoriqueCommande.objects

        .select_related(
            "compteur"
        )

        .order_by(
            "-date_action"
        )[:100]

    )


    return render(

        request,

        "compteur/admin/historique.html",

        {
            "historique": historique
        }
    )


# ============================================================
# API PZEM - RECEPTION DES MESURES ESP32
# ============================================================

@csrf_exempt
def api_pzem_mesure(request):

    # ========================================================
    # MÉTHODE HTTP
    # ========================================================

    if request.method != "POST":

        return JsonResponse({

            "success": False,

            "message":
                "Méthode POST uniquement."

        }, status=405)


    try:

        # ====================================================
        # LECTURE DES DONNÉES ESP32
        # ====================================================

        data = json.loads(
            request.body
        )


        device_id = data.get(
            "device_id"
        )

        tension = data.get(
            "tension"
        )

        courant = data.get(
            "courant"
        )

        puissance = data.get(
            "puissance"
        )

        energie = data.get(
            "energie"
        )


        # ====================================================
        # VÉRIFICATION DEVICE ID
        # ====================================================

        if not device_id:

            return JsonResponse({

                "success": False,

                "message":
                    "device_id obligatoire."

            }, status=400)


        # ====================================================
        # RECHERCHE DU COMPTEUR
        # ====================================================

        compteur = (
            Compteur.objects
            .filter(
                device_id=device_id
            )
            .first()
        )


        if not compteur:

            return JsonResponse({

                "success": False,

                "message":
                    "Compteur introuvable."

            }, status=404)


        # ====================================================
        # CONVERSION ÉNERGIE PZEM
        # ====================================================

        energie_actuelle = Decimal(

            str(
                energie or 0
            )

        )


        # ====================================================
        # DERNIÈRE MESURE
        # ====================================================

        derniere_mesure = (

            Mesure.objects

            .filter(
                compteur=compteur
            )

            .order_by(
                "-date_mesure"
            )

            .first()

        )


        # ====================================================
        # CALCUL DE LA CONSOMMATION
        # ====================================================

        consommation = Decimal(
            "0.000"
        )


        if derniere_mesure:

            energie_precedente = Decimal(

                str(
                    derniere_mesure.energie
                    or 0
                )

            )


            consommation = (

                energie_actuelle

                - energie_precedente

            )


            # ------------------------------------------------
            # PROTECTION VALEUR NÉGATIVE
            # ------------------------------------------------

            if consommation < 0:

                consommation = Decimal(
                    "0.000"
                )


        # ====================================================
        # ENREGISTREMENT DE LA MESURE
        # ====================================================

        mesure = Mesure.objects.create(

            compteur=compteur,

            tension=tension or 0,

            courant=courant or 0,

            puissance=puissance or 0,

            energie=energie_actuelle

        )


        # ====================================================
        # CONSOMMATION TOTALE
        # ====================================================

        compteur.consommation_totale = (
            energie_actuelle
        )


        # ====================================================
        # DÉDUCTION DU SOLDE
        # ====================================================

        if consommation > 0:

            solde_avant = (

                compteur.solde

                or Decimal("0.000")

            )


            solde_apres = (

                solde_avant

                - consommation

            )


            # ------------------------------------------------
            # LE SOLDE NE DESCEND PAS SOUS ZERO
            # ------------------------------------------------

            if solde_apres < 0:

                solde_apres = Decimal(
                    "0.000"
                )


            compteur.solde = (
                solde_apres
            )


            # =================================================
            # HISTORIQUE CONSOMMATION
            # =================================================

            MouvementSolde.objects.create(

                compteur=compteur,

                type_operation="CONSOMMATION",

                quantite=consommation,

                motif="Consommation PZEM",

                solde_avant=solde_avant,

                solde_apres=solde_apres

            )


        # ====================================================
        # STATUT ESP32
        # ====================================================

        compteur.esp32_connecte = True

        compteur.derniere_connexion = (
            timezone.now()
        )


        # ====================================================
        # SAUVEGARDE
        # ====================================================

        compteur.save()


        # ====================================================
        # RÉPONSE API
        # ====================================================

        return JsonResponse({

            "success": True,

            "message":
                "Mesure PZEM enregistrée.",

            "device_id":
                device_id,

            "mesure_id":
                mesure.id,

            "energie":
                float(
                    energie_actuelle
                ),

            "consommation":
                float(
                    consommation
                ),

            "solde":
                float(
                    compteur.solde
                ),

            "autorisation":
                compteur.autorisation,

            "contacteur":
                compteur.contacteur,

        })


    except Exception as e:

        return JsonResponse({

            "success": False,

            "message":
                str(e)

        }, status=400)


# ============================================================
# API TEMPS REEL
# ============================================================

@login_required
def api_temps_reel(request):

    # ========================================================
    # COMPTEURS
    # ========================================================

    if request.user.is_staff:

        compteurs = (
            Compteur.objects.all()
        )

    else:

        compteurs = (
            Compteur.objects.filter(
                utilisateur=request.user
            )
        )


    resultats = []


    # ========================================================
    # TRAITEMENT DES COMPTEURS
    # ========================================================

    for compteur in compteurs:

        # ====================================================
        # DERNIÈRES 24 MESURES
        # ====================================================

        mesures = list(

            Mesure.objects

            .filter(
                compteur=compteur
            )

            .order_by(
                "-date_mesure"
            )[:24]

        )


        # ====================================================
        # DERNIÈRE MESURE
        # ====================================================

        derniere_mesure = (

            mesures[0]

            if mesures

            else None

        )


        # ====================================================
        # ORDRE CHRONOLOGIQUE
        # ====================================================

        mesures.reverse()


        historique = []


        # ====================================================
        # CONSTRUCTION HISTORIQUE
        # ====================================================

        for mesure in mesures:

            historique.append({

                "tension":
                    float(
                        mesure.tension
                    ),

                "courant":
                    float(
                        mesure.courant
                    ),

                "puissance":
                    float(
                        mesure.puissance
                    ),

                "energie":
                    float(
                        mesure.energie
                    ),

                "date_mesure":
                    mesure.date_mesure.isoformat(),

                "heure":
                    mesure.date_mesure.strftime(
                        "%H:%M:%S"
                    ),

            })


        # ====================================================
        # RÉSULTAT COMPTEUR
        # ====================================================

        resultats.append({

            "id":
                compteur.id,

            "device_id":
                compteur.device_id,

            "nom":
                compteur.nom,

            "solde":
                float(
                    compteur.solde
                ),

            "consommation_totale":
                float(
                    compteur.consommation_totale
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

            # =================================================
            # DERNIÈRE MESURE
            # =================================================

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

            # =================================================
            # HISTORIQUE POUR LES COURBES
            # =================================================

            "mesures":
                historique,

        })


    # ========================================================
    # RÉPONSE JSON
    # ========================================================

    return JsonResponse({

        "success":
            True,

        "compteurs":
            resultats,

    })

