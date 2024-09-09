# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import FormulaireConnexionPersonnalise, FormulaireInscription
from django.contrib.auth.decorators import login_required
from .models import Etudiant


def vue_connexion(request):
    if request.method == 'POST':
        formulaire = FormulaireConnexionPersonnalise(request, data=request.POST)
        if formulaire.is_valid():
            # Authentifier l'utilisateur
            nom_utilisateur = formulaire.cleaned_data['username']
            mot_de_passe = formulaire.cleaned_data['password']
            utilisateur = authenticate(username=nom_utilisateur, password=mot_de_passe)
            if utilisateur is not None:
                login(request, utilisateur)
                return redirect('accueil')  # Redirige vers la page d'accueil ou une autre page après connexion
    else:
        formulaire = FormulaireConnexionPersonnalise()

    return render(request, 'connexion.html', {'formulaire': formulaire})



def vue_inscription(request):
    if request.method == 'POST':
        formulaire = FormulaireInscription(request.POST)
        if formulaire.is_valid():
            formulaire.save()
            return redirect('connexion')  # Redirige vers la page de connexion après inscription
    else:
        formulaire = FormulaireInscription()

    return render(request, 'inscription.html', {'formulaire': formulaire})



@login_required
def vue_accueil(request):
    utilisateur = request.user
    etudiant = Etudiant.objects.get(username=utilisateur.username)
    
    # Récupérer les informations pertinentes
    cours = etudiant.get_promotions_courses()
    examens = []
    interrogations = []
    travaux_pratiques = []

    for cours in cours:
        examens.extend(cours.examen_set.all())
        interrogations.extend(cours.interrogation_set.all())
        travaux_pratiques.extend(cours.travailpratique_set.all())
    
    context = {
        'etudiant': etudiant,
        'cours': cours,
        'examens': examens,
        'interrogations': interrogations,
        'travaux_pratiques': travaux_pratiques,
    }

    return render(request, 'accueil.html', context)