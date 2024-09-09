from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import DemandePasseport, Paiement
from .utils import envoyer_notification_email

@receiver(post_save, sender=Paiement)
def notifier_paiement(sender, instance, created, **kwargs):
    if created:
        demande = instance.demande_passeport

        # Génération du numéro de demande après le paiement
        if demande.numero_demande is None:
            demande.numero_demande = demande.generer_numero_unique()
            demande.save()

        # Notification de la demande créée
        sujet_creation = 'Votre demande de passeport a été reçue'
        message_template_creation = 'email_demande_creation.html'
        context_creation = {
            'prenom': demande.personne.prenom if demande.personne else 'Inconnu',
            'nom': demande.personne.nom if demande.personne else 'Inconnu',
            'numero_demande': demande.numero_demande
        }
        envoyer_notification_email(demande.personne.email, sujet_creation, message_template_creation, context_creation)

        # Planifier les rendez-vous après paiement
        demande.planifier_rendez_vous()

        # Notification du rendez-vous ANR
        if demande.date_rendez_vous_anr:
            sujet_anr = 'Votre rendez-vous avec ANR a été planifié'
            message_template_anr = 'email_rendez_vous_anr.html'
            context_anr = {
                'prenom': demande.personne.prenom,
                'nom': demande.personne.nom,
                'date_rendez_vous_anr': demande.date_rendez_vous_anr
            }
            envoyer_notification_email(demande.personne.email, sujet_anr, message_template_anr, context_anr)

        # Notification du rendez-vous avec le ministère
        if demande.date_rendez_vous_ministere:
            sujet_ministere = 'Votre rendez-vous avec le ministère a été planifié'
            message_template_ministere = 'email_rendez_vous_ministere.html'
            context_ministere = {
                'prenom': demande.personne.prenom,
                'nom': demande.personne.nom,
                'date_rendez_vous_ministere': demande.date_rendez_vous_ministere
            }
            envoyer_notification_email(demande.personne.email, sujet_ministere, message_template_ministere, context_ministere)
