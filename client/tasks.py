# fichier pour les taches Celery

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import DemandePasseport

@shared_task
def envoyer_rappel_rendez_vous_anr(demande_id):
    try:
        demande = DemandePasseport.objects.get(id=demande_id)
        if demande.date_rendez_vous_anr and demande.date_rendez_vous_anr.date() == timezone.now().date():
            sujet = 'Rappel de votre rendez-vous avec ANR'
            message = f'Bonjour {demande.utilisateur.first_name},\n\nVotre rendez-vous avec ANR est prévu pour aujourd\'hui à {demande.date_rendez_vous_anr}.'
            send_mail(
                sujet,
                message,
                'rameaumambu1@gmail.com',
                [demande.personne.email],
                fail_silently=False,
            )
    except DemandePasseport.DoesNotExist:
        pass
