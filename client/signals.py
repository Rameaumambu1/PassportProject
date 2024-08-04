
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import DemandePasseport


from .utils import envoyer_notification_email


@receiver(post_save, sender=DemandePasseport)
def envoyer_notification_demande(sender, instance, created, **kwargs):
    if created:
        numero_demande = instance.numero_demande
        utilisateur_email = instance.utilisateur.email
        send_mail(
            'Votre demande de passeport a été reçue',
            f'Votre numéro de demande est : {numero_demande}',
            'noreply@votreapplication.com',  # Adresse e-mail de l'expéditeur
            [utilisateur_email],
            fail_silently=False,
        )


def envoyer_notification_rendez_vous(sender, instance, **kwargs):
    if instance.date_rendez_vous_anr and instance.date_rendez_vous_ministere:
        if kwargs.get('created', False):
            # Notification lors de la création
            sujet_anr = 'Votre rendez-vous avec ANR a été planifié'
            message_template_anr = 'email_rendez_vous_anr.html'
            context_anr = {
                'prenom': instance.utilisateur.first_name,
                'nom': instance.utilisateur.last_name,
                'date_rendez_vous_anr': instance.date_rendez_vous_anr
            }
            envoyer_notification_email(instance.utilisateur.email, sujet_anr, message_template_anr, context_anr)

            sujet_ministere = 'Votre rendez-vous avec le ministère a été planifié'
            message_template_ministere = 'email_rendez_vous_ministere.html'
            context_ministere = {
                'prenom': instance.utilisateur.first_name,
                'nom': instance.utilisateur.last_name,
                'date_rendez_vous_ministere': instance.date_rendez_vous_ministere
            }
            envoyer_notification_email(instance.utilisateur.email, sujet_ministere, message_template_ministere, context_ministere)
