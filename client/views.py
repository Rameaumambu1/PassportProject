
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import DemandePasseport, Paiement, StatutANR, StatutMinistere, Personne
from .forms import DemandePasseportForm, PaiementForm, StatutANRForm, StatutMinistereForm, PersonneForm, VerifierStatutForm


def home(request):
    demandes = DemandePasseport.objects.all()

    return render(request, 'index.html', {'demandes': demandes})



# def connexion(request):
#     return render(request, 'connexion.html')

# def demande(request):

#     return render(request, 'demande.html')



def demande_list(request):
    demandes = DemandePasseport.objects.all()
    return render(request, 'demande_list.html', {'demandes':demandes})

# def personne_create(request):
#     if request.method == 'POST':
#         formP = PersonneForm(request.POST)
#         if formP.is_valid():
#             requerant = formP.save(commit=False)
#             # demande.utilisateur = request.user  # Assurez-vous que l'utilisateur est bien assigné
           
#             requerant.save()

            
#             return redirect('demande_create')  # Redirection correcte vers la liste des demandes
#     else:
#         formP = PersonneForm()
#     return render(request, 'personne_create.html', {'formP': formP})
def personne_create(request):
    if request.method == 'POST':
        formP = PersonneForm(request.POST, request.FILES)
        if formP.is_valid():
            requerant = formP.save()
            return redirect('demande_create', personne_id=requerant.id)
    else:
        formP = PersonneForm()
    return render(request, 'personne_create.html', {'formP': formP})




# def demande_create(request):
#     if request.method == 'POST':
#         form = DemandePasseportForm(request.POST)
#         if form.is_valid():
#             demande = form.save(commit=False)
#             # demande.utilisateur = request.user  # Assurez-vous que l'utilisateur est bien assigné
           
#             demande.save()
#             return redirect('demande_list')  # Redirection correcte vers la liste des demandes
#     else:
#         form = DemandePasseportForm()
#     return render(request, 'demande_create.html', {'form': form})
def demande_create(request, personne_id=None):
    last_personne = None
    if personne_id:
        last_personne = get_object_or_404(Personne, id=personne_id)

    if request.method == 'POST':
        form = DemandePasseportForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            if last_personne:
                demande.personne = last_personne
            demande.save()
            return redirect('paiement_view', demande_id=demande.id)
    else:
        form = DemandePasseportForm()
    
    return render(request, 'demande_create.html', {'form': form, 'last_personne': last_personne})



def demande_detail(request, demande_id):
    demande = DemandePasseport.objects.get(id=demande_id)
    # statut_anr = StatutANR.objects.get(demande_id=demande_id)


    # Vérifie si les champs spécifiques sont remplis ou non
    champ_non_rempli = {
        'anr_rendez_vous_complet': demande.anr_rendez_vous_complet is None,
        'date_paiement': demande.date_paiement is None,
        'date_revision': demande.date_revision is None,
        'date_finalisation': demande.date_finalisation is None,
        'date_rejet': demande.date_rejet is None,
        'date_rendez_vous_anr': demande.date_rendez_vous_anr is None,
        'date_rendez_vous_ministere': demande.date_rendez_vous_ministere is None
    }
    
    
    

    context = {
        'demande': demande,
        
        'champ_non_rempli': champ_non_rempli
    }
    return render(request, 'demande_detail.html', context)




@login_required
def paiement_view(request, demande_id):
    """Vue pour gérer le paiement d'une demande de passeport."""
    demande = get_object_or_404(DemandePasseport, id=demande_id)
    
    if request.method == 'POST':
        formPaie = PaiementForm(request.POST)
        if formPaie.is_valid():
            paie = formPaie.save(commit=False)
            paie.montant = 199
            paie.save()
        
        # paiement = Paiement(demande_passeport=demande, montant=montant)
        

        # Met à jour la demande de passeport après le paiement
        demande.date_paiement = timezone.now()
        demande.statut = 'payee'
        demande.save()

        # Notification de la demande 
        demande.notifier_creation()
        
        # Planifie automatiquement les rendez-vous
        demande.planifier_rendez_vous()

        messages.success(request, 'Paiement effectué et rendez-vous planifiés.')
        # return redirect('demande_detail', demande_id=demande_id)
        return redirect('demande_detail', demande_id)

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


def verifier_statut(request):
    # statut = None
    # demande = None
    if request.method == 'POST':
        form = VerifierStatutForm(request.POST)
        if form.is_valid():
            numero_demande = form.cleaned_data['numero_demande']
            demande = get_object_or_404(DemandePasseport, numero_demande=numero_demande)
            # statut = demande.statut
            return redirect('demande_detail', demande_id=demande.id)
    else:
        form = VerifierStatutForm()
    
    return render(request, 'verifier_statut.html', {
        'form': form,
        'demande': None,
        'statut': None
    })


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
