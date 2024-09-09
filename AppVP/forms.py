# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import Etudiant, Promotion


class FormulaireConnexionPersonnalise(AuthenticationForm):
    numero_promotion = forms.CharField(max_length=14, required=True, label="Numéro de Promotion")

    def confirmer_authentification_autorisee(self, utilisateur):
        # Vérifier que le numéro de promotion est correct pour l'utilisateur
        numero_promotion = self.cleaned_data.get('numero_promotion')
        if utilisateur.promotion.numero != numero_promotion:
            raise forms.ValidationError(
                "Le numéro de promotion fourni est incorrect.",
                code='invalid_login',
            )


class FormulaireInscription(UserCreationForm):
    class Meta:
        model = Etudiant
        fields = ('username', 'numero_promotion')  # Indique les champs nécessaires ici

    