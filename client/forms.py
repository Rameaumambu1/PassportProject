from django import forms
from .models import DemandePasseport, Personne, Paiement, StatutANR, StatutMinistere

class PersonneForm(forms.ModelForm):
    """Formulaire pour entrer les informations sur la personne si la demande est pour quelqu'un d'autre."""

    class Meta:
        model = Personne
        fields = ['nom', 'prenom', 'date_naissance', 'adresse', 'email']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class DemandePasseportForm(forms.ModelForm):
    """Formulaire pour créer ou mettre à jour une demande de passeport."""

    class Meta:
        model = DemandePasseport
        fields = [
            'personne', 'est_pour_moi', 'statut', 'date_paiement', 'date_revision',
            'date_finalisation', 'date_rejet', 'date_rendez_vous_anr', 
            'date_rendez_vous_ministere', 'anr_rendez_vous_complet'
        ]
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_revision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_finalisation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_rejet': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_rendez_vous_anr': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_rendez_vous_ministere': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'anr_rendez_vous_complet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        """Initialise le formulaire en fonction de la demande pour soi-même ou pour quelqu'un d'autre."""
        include_personne_form = kwargs.pop('include_personne_form', False)
        super().__init__(*args, **kwargs)
        if not include_personne_form:
            # Exclure le champ 'personne' si la demande est pour soi-même
            self.fields.pop('personne')

    def clean(self):
        """Valide les données du formulaire."""
        cleaned_data = super().clean()
        if cleaned_data.get('est_pour_moi') and cleaned_data.get('personne'):
            raise forms.ValidationError("La personne ne doit pas être spécifiée si la demande est pour vous.")
        return cleaned_data

class PaiementForm(forms.ModelForm):
    """Formulaire pour saisir les informations de paiement pour une demande de passeport."""

    class Meta:
        model = Paiement
        fields = ['montant']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class StatutANRForm(forms.ModelForm):
    """Formulaire pour mettre à jour le statut du rendez-vous avec la société ANR."""

    class Meta:
        model = StatutANR
        fields = ['rendez_vous_complet']
        widgets = {
            'rendez_vous_complet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class StatutMinistereForm(forms.ModelForm):
    """Formulaire pour mettre à jour le statut de la demande au ministère."""

    class Meta:
        model = StatutMinistere
        fields = ['rendez_vous_programme', 'date_finalisation', 'passeport_livre']
        widgets = {
            'rendez_vous_programme': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_finalisation': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'passeport_livre': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
