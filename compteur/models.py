from django.db import models
from django.contrib.auth.models import User


class Profil(models.Model):
    utilisateur = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profil"
    )

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    fokontany = models.CharField(max_length=100, blank=True)

    telephone = models.CharField(max_length=30, blank=True)

    date_naissance = models.DateField(
        null=True,
        blank=True
    )

    profession = models.CharField(
        max_length=100,
        blank=True
    )

    cin = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    photo_cin_recto = models.ImageField(
        upload_to="clients/cin/recto/",
        null=True,
        blank=True
    )

    photo_cin_verso = models.ImageField(
        upload_to="clients/cin/verso/",
        null=True,
        blank=True
    )

    photo_user = models.ImageField(
        upload_to="clients/photos/",
        null=True,
        blank=True
    )

    cin_verifiee = models.BooleanField(default=False)
    telephone_verifie = models.BooleanField(default=False)
    email_verifie = models.BooleanField(default=False)

    actif = models.BooleanField(default=True)

    date_inscription = models.DateTimeField(
        auto_now_add=True
    )

    date_modification = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Compteur(models.Model):

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="compteurs"
    )

    device_id = models.CharField(
        max_length=50,
        unique=True
    )

    nom = models.CharField(
        max_length=100,
        default="Compteur ELEC"
    )

    # Solde disponible en kWh
    solde = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0
    )

    # Consommation totale en kWh
    consommation_totale = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    # Autorisation générale
    autorisation = models.BooleanField(
        default=True
    )

    # État du contacteur
    contacteur = models.BooleanField(
        default=True
    )

    # État de connexion ESP32
    esp32_connecte = models.BooleanField(
        default=False
    )

    derniere_connexion = models.DateTimeField(
        null=True,
        blank=True
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.device_id} - {self.nom}"


class Mesure(models.Model):

    compteur = models.ForeignKey(
        Compteur,
        on_delete=models.CASCADE,
        related_name="mesures"
    )

    tension = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    courant = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        default=0
    )

    puissance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    energie = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    date_mesure = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.compteur.device_id} - "
            f"{self.date_mesure}"
        )


class HistoriqueCommande(models.Model):

    ACTION_CHOICES = [
        ("ON", "Mise sous tension"),
        ("OFF", "Coupure"),
    ]

    compteur = models.ForeignKey(
        Compteur,
        on_delete=models.CASCADE,
        related_name="historique_commandes"
    )

    action = models.CharField(
        max_length=3,
        choices=ACTION_CHOICES
    )

    motif = models.CharField(
        max_length=255,
        blank=True
    )

    date_action = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.compteur.device_id} - "
            f"{self.action}"
        )



# gestion du solde kWh.
class MouvementSolde(models.Model):

    TYPE_CHOICES = [
        ("RECHARGE", "Recharge"),
        ("CONSOMMATION", "Consommation"),
        ("AJUSTEMENT", "Ajustement"),
    ]

    compteur = models.ForeignKey(
        Compteur,
        on_delete=models.CASCADE,
        related_name="mouvements_solde"
    )

    type_operation = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    quantite = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    motif = models.CharField(
        max_length=255,
        blank=True
    )

    solde_avant = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0
    )

    solde_apres = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0
    )

    date_operation = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.compteur.device_id} - "
            f"{self.type_operation} - "
            f"{self.quantite} kWh"
        )

