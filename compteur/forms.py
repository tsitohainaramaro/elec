from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profil


# ============================================================
# CRÉATION D'UN CLIENT
# ============================================================

class ClientCreationForm(UserCreationForm):

    email = forms.EmailField(
        required=False,
        label="Email"
    )

    nom = forms.CharField(
        max_length=100,
        label="Nom"
    )

    prenom = forms.CharField(
        max_length=100,
        label="Prénom"
    )

    telephone = forms.CharField(
        max_length=30,
        required=False,
        label="Téléphone"
    )

    adresse = forms.CharField(
        required=False,
        label="Adresse",
        widget=forms.Textarea(attrs={
            "rows": 3
        })
    )

    ville = forms.CharField(
        max_length=100,
        required=False,
        label="Ville"
    )

    fokontany = forms.CharField(
        max_length=100,
        required=False,
        label="Fokontany"
    )

    date_naissance = forms.DateField(
        required=False,
        label="Date de naissance",
        widget=forms.DateInput(
            attrs={
                "type": "date"
            }
        )
    )

    profession = forms.CharField(
        max_length=100,
        required=False,
        label="Profession"
    )

    cin = forms.CharField(
        max_length=50,
        required=False,
        label="CIN"
    )

    photo_cin_recto = forms.ImageField(
        required=False,
        label="Photo CIN recto"
    )

    photo_cin_verso = forms.ImageField(
        required=False,
        label="Photo CIN verso"
    )

    photo_user = forms.ImageField(
        required=False,
        label="Photo du client"
    )

    actif = forms.BooleanField(
        required=False,
        initial=True,
        label="Compte actif"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nom d'utilisateur"
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmation du mot de passe"

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data.get("email", "")

        if commit:
            user.save()

            Profil.objects.create(
                utilisateur=user,
                nom=self.cleaned_data["nom"],
                prenom=self.cleaned_data["prenom"],
                adresse=self.cleaned_data.get("adresse", ""),
                ville=self.cleaned_data.get("ville", ""),
                fokontany=self.cleaned_data.get("fokontany", ""),
                telephone=self.cleaned_data.get("telephone", ""),
                date_naissance=self.cleaned_data.get("date_naissance"),
                profession=self.cleaned_data.get("profession", ""),
                cin=self.cleaned_data.get("cin") or None,
                photo_cin_recto=self.cleaned_data.get("photo_cin_recto"),
                photo_cin_verso=self.cleaned_data.get("photo_cin_verso"),
                photo_user=self.cleaned_data.get("photo_user"),
                actif=self.cleaned_data.get("actif", True),
            )

        return user


# ============================================================
# MODIFICATION D'UN CLIENT
# ============================================================

class ClientUpdateForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur"
    )

    email = forms.EmailField(
        required=False,
        label="Email"
    )

    class Meta:
        model = Profil

        fields = [
            "nom",
            "prenom",
            "telephone",
            "adresse",
            "ville",
            "fokontany",
            "date_naissance",
            "profession",
            "cin",
            "photo_cin_recto",
            "photo_cin_verso",
            "photo_user",
            "actif",
        ]

        widgets = {
            "adresse": forms.Textarea(
                attrs={
                    "rows": 3
                }
            ),

            "date_naissance": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        profil = self.instance

        if profil and profil.utilisateur:
            self.fields["username"].initial = (
                profil.utilisateur.username
            )

            self.fields["email"].initial = (
                profil.utilisateur.email
            )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        user = self.instance.utilisateur

        existe = (
            User.objects
            .filter(username=username)
            .exclude(pk=user.pk)
            .exists()
        )

        if existe:
            raise forms.ValidationError(
                "Ce nom d'utilisateur existe déjà."
            )

        return username

    def clean_cin(self):
        cin = self.cleaned_data.get("cin")

        if not cin:
            return None

        cin = cin.strip()

        existe = (
            Profil.objects
            .filter(cin=cin)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if existe:
            raise forms.ValidationError(
                "Cette CIN est déjà utilisée par un autre client."
            )

        return cin

    def save(self, commit=True):
        profil = super().save(commit=False)

        user = profil.utilisateur

        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data.get("email", "")

        if commit:
            user.save()
            profil.save()

        return profil