from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'index.html')



def connexion(request):
    return render(request, 'connexion.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import DemandePasseport, Paiement, StatutANR, StatutMinistere, Personne
from .forms import DemandePasseportForm, PaiementForm, StatutANRForm, StatutMinistereForm

@login_required
def demande_passeport_create(request):
    """Vue pour créer une nouvelle demande de passeport."""
    if request.method == 'POST':
        form = DemandePasseportForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.utilisateur = request.user
            demande.save()
            
            # Notifier la personne concernée s'il s'agit d'une demande pour quelqu'un d'autre
            demande.notifier_personne()

            messages.success(request, 'Demande de passeport créée avec succès.')
            return redirect('demande_detail', demande_id=demande.id)
    else:
        form = DemandePasseportForm()
    return render(request, 'demande_passeport_form.html', {'form': form})

@login_required
def demande_passeport_detail(request, demande_id):
    """Vue pour afficher les détails d'une demande de passeport."""
    demande = get_object_or_404(DemandePasseport, id=demande_id)
    return render(request, 'demande_passeport_detail.html', {'demande': demande})

@login_required
def paiement_view(request, demande_id):
    """Vue pour gérer le paiement d'une demande de passeport."""
    demande = get_object_or_404(DemandePasseport, id=demande_id)
    
    if request.method == 'POST':
        montant = request.POST.get('montant')
        paiement = Paiement(demande_passeport=demande, montant=montant)
        paiement.save()

        # Met à jour la demande de passeport après le paiement
        demande.date_paiement = timezone.now()
        demande.statut = 'payee'
        demande.save()

        # Planifie automatiquement les rendez-vous
        demande.planifier_rendez_vous()

        messages.success(request, 'Paiement effectué et rendez-vous planifiés.')
        return redirect('demande_detail', demande_id=demande_id)

    return render(request, 'paiement_form.html', {'demande': demande})

@login_required
def statut_anr_view(request, demande_id):
    """Vue pour mettre à jour le statut du rendez-vous avec ANR."""
    demande = get_object_or_404(DemandePasseport, id=demande_id)
    
    if request.method == 'POST':
        statut_anr, created = StatutANR.objects.get_or_create(demande_passeport=demande)
        statut_anr.rendez_vous_complet = request.POST.get('rendez_vous_complet') == 'on'
        statut_anr.date_confirmation = timezone.now()
        statut_anr.save()

        # Met à jour la demande de passeport
        demande.anr_rendez_vous_complet = statut_anr.rendez_vous_complet
        demande.planifier_rendez_vous()
        demande.save()

        messages.success(request, 'Statut du rendez-vous ANR mis à jour.')
        return redirect('demande_detail', demande_id=demande_id)

    form = StatutANRForm(instance=demande.statut_anr if hasattr(demande, 'statut_anr') else None)
    return render(request, 'statut_anr_form.html', {'form': form, 'demande': demande})

@login_required
def statut_ministere_view(request, demande_id):
    """Vue pour mettre à jour le statut de la demande au ministère."""
    demande = get_object_or_404(DemandePasseport, id=demande_id)
    
    if request.method == 'POST':
        statut_ministere, created = StatutMinistere.objects.get_or_create(demande_passeport=demande)
        statut_ministere.rendez_vous_programme = request.POST.get('rendez_vous_programme') == 'on'
        statut_ministere.date_finalisation = request.POST.get('date_finalisation')
        statut_ministere.passeport_livre = request.POST.get('passeport_livre') == 'on'
        statut_ministere.save()

        messages.success(request, 'Statut de la demande au ministère mis à jour.')
        return redirect('demande_detail', demande_id=demande_id)

    form = StatutMinistereForm(instance=demande.statut_ministere if hasattr(demande, 'statut_ministere') else None)
    return render(request, 'statut_ministere_form.html', {'form': form, 'demande': demande})
