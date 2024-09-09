from venv import logger
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .utils import envoyer_notification_email
import uuid
from django.core.exceptions import ValidationError


# Create your models here.

class Personne(models.Model):
    """Représente une personne pour laquelle une demande de passeport peut être faite."""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    lieu_naissance = models.CharField(max_length=100)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=100)
    etat_civil = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    adresse_residence = models.CharField(max_length=100)
    email = models.EmailField()

    couleur_des_yeux = models.CharField(max_length=100)
    taille = models.CharField(max_length=100)
    signe_particulier = models.CharField(max_length=100)
    nom_du_pere = models.CharField(max_length=100)
    postnom_du_pere = models.CharField(max_length=100)
    prenom_du_pere = models.CharField(max_length=100)
    nom_de_la_mere = models.CharField(max_length=100)
    postnom_de_la_mere = models.CharField(max_length=100)
    prenom_de_la_mere = models.CharField(max_length=100)
    groupe_ethnique = models.CharField(max_length=100)
    localite_origine = models.CharField(max_length=100)
    territoire = models.CharField(max_length=100)
    secteur = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    nationalite_origine = models.CharField(max_length=100)
    nationalite_actuelle = models.CharField(max_length=100)

    image_signature_du_requerant = models.ImageField(upload_to="images/")


    def __str__(self):
        return f"{self.prenom} {self.nom}"



class DemandePasseport(models.Model):
    """Représente une demande de passeport."""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('en_revision', 'En révision'),
        ('terminee', 'Terminée'),
        ('rejettee', 'Rejetée'),
        ('annulee', 'Annulée'),
    ]
    
    # utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE, null=True, blank=True)
    est_pour_moi = models.BooleanField(default=False)
    numero_demande = models.CharField(max_length=100, unique=True, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(blank=True, null=True)
    date_revision = models.DateTimeField(blank=True, null=True)
    date_finalisation = models.DateTimeField(blank=True, null=True)
    date_rejet = models.DateTimeField(blank=True, null=True)
    date_rendez_vous_anr = models.DateTimeField(blank=True, null=True)
    date_rendez_vous_ministere = models.DateTimeField(blank=True, null=True)
    anr_rendez_vous_complet = models.BooleanField(default=False)  # Pour vérifier que le rendez-vous ANR a eu lieu

    def __str__(self):
        if self.personne:
            return f"Demande {self.numero_demande} pour {self.personne.prenom} {self.personne.nom} Demande #{self.id}"
        return f"Demande {self.numero_demande} pour une personne inconnue Demande #{self.id}"


    # def __str__(self):
        
    #     return f"Demande {self.numero_demande} pour {self.personne.prenom} {self.personne.nom} Demande #{self.id}"


    
       


    def save(self, *args, **kwargs):
        if not self.personne:
            raise ValidationError("La demande doit être liée à une personne.")
        
        super().save(*args, **kwargs)  # Enregistrez d'abord sans le numéro unique
        if self.statut == 'payee' and not self.numero_demande:
            self.numero_demande = self.generer_numero_unique()
            super().save(*args, **kwargs)  # Enregistrez à nouveau avec le numéro unique

        

    def generer_numero_unique(self):
        """Génère un numéro de demande unique."""
        while True:
            numero = str(uuid.uuid4().hex[:10].upper())
            if not DemandePasseport.objects.filter(numero_demande=numero).exists():
                return numero


    def notifier_creation(self):
        """Envoie une notification par e-mail lorsque le paiement est effectué et la demande est créée."""
        sujet = 'Votre demande de passeport a été créée'
        message_template = 'email_demande_creation.html'  # Assurez-vous que ce template existe
        context = {
            'prenom': self.personne.prenom if self.personne else 'Inconnu',
            'nom': self.personne.nom if self.personne else 'Inconnu',
            'numero_demande': self.numero_demande or 'Non attribué'
        }
        
        # Assurez-vous que l'adresse e-mail du modèle `Personne` est disponible
        if self.personne and self.personne.email:
            message_html = render_to_string(message_template, context)
            send_mail(
                sujet,
                '',  # Corps du message en texte brut, laissez vide si vous n'en avez pas
                'rameaumambu1@gmail.com',  # Remplacez par l'adresse e-mail de l'expéditeur
                [self.personne.email],
                fail_silently=False,
                html_message=message_html
            )




    def planifier_rendez_vous(self):
        """Planifie automatiquement les rendez-vous et envoie des notifications."""
        
        if self.date_paiement and not self.date_rendez_vous_anr:
            # Planifie le rendez-vous avec ANR deux jours après la validation du paiement
            self.date_rendez_vous_anr = self.date_paiement + timedelta(days=2)
            self.save()

            # Crée un rendez-vous ANR dans la table RendezVousANR
            rendez_vous_anr, created = RendezVousANR.objects.get_or_create(
                demande_passeport=self,
                defaults={'date_programmee': self.date_rendez_vous_anr}
            )
            if created:
                # Envoyer une notification par e-mail pour le rendez-vous ANR
                sujet = 'Votre rendez-vous avec ANR a été planifié'
                message_template = 'email_rdv_anr.html'
                context = {
                    'prenom': self.personne.prenom,
                    'nom': self.personne.nom,
                    'date_rendez_vous_anr': self.date_rendez_vous_anr
                }
                envoyer_notification_email(self.personne.email, sujet, message_template, context)


            

        if self.date_rendez_vous_anr and not self.date_rendez_vous_ministere and self.anr_rendez_vous_complet:
            # Planifie le rendez-vous avec le ministère deux jours après le rendez-vous ANR
            self.date_rendez_vous_ministere = self.date_rendez_vous_anr + timedelta(days=2)
            self.save()
            # Envoyer une notification par e-mail pour le rendez-vous avec le ministère
            sujet = 'Votre rendez-vous avec le ministère a été planifié'
            message_template = 'email_rdv_ministere.html'
            context = {
                'prenom': self.personne.prenom,
                'nom': self.personne.nom,
                'date_rendez_vous_ministere': self.date_rendez_vous_ministere
            }
            envoyer_notification_email(self.personne.email, sujet, message_template, context)

    def verifier_rendez_vous_anr(self):
        """Vérifie automatiquement si le rendez-vous ANR est raté."""
        if self.date_rendez_vous_anr:
            date_limite = self.date_rendez_vous_anr + timedelta(days=1)
            if timezone.now() > date_limite and not self.anr_rendez_vous_complet:
                self.statut = 'annulee'
                self.save()


    

from django.core.mail import send_mail
from django.template.loader import render_to_string

class Paiement(models.Model):
    """Représente le paiement pour une demande de passeport."""
    demande_passeport = models.OneToOneField(DemandePasseport, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Vérifier si le montant est exactement 199
        if self.montant != 199:
            raise ValidationError("Le montant du paiement doit être exactement 199.")

        # Si la date de paiement n'est pas définie, la définir à l'heure actuelle
        if not self.date_paiement:
            self.date_paiement = timezone.now()
        super().save(*args, **kwargs)

        # Met à jour le statut de la demande de passeport
        self.demande_passeport.statut = 'payee'
        self.demande_passeport.date_paiement = self.date_paiement
        self.demande_passeport.save()  # Enregistrez d'abord le statut mis à jour

         # Envoyer la notification de création de la demande
        # logger.info("Appel de notifier_creation")
        self.notifier_creation()  # Ajoutez ceci pour vérifier si la méthode est appelée


        # Planifier les rendez-vous
        self.demande_passeport.planifier_rendez_vous()
        self.demande_passeport.save()  # Enregistrez à nouveau pour mettre à jour les rendez-vous

    

    def notifier_creation(self):
        """Envoie une notification par e-mail lorsque le paiement est effectué et la demande est créée."""
        sujet = 'Votre demande de passeport a été créée'
        message_template = 'email_demande_creation.html'  # Assurez-vous que ce template existe
        context = {
            'prenom': self.demande_passeport.personne.prenom if self.demande_passeport.personne else 'Inconnu',
            'nom': self.demande_passeport.personne.nom if self.demande_passeport.personne else 'Inconnu',
            'numero_demande': self.demande_passeport.numero_demande or 'Non attribué'
        }
        
        if self.demande_passeport.personne and self.demande_passeport.personne.email:
            message_html = render_to_string(message_template, context)
            send_mail(
                sujet,
                '',  # Corps du message en texte brut, laissez vide si vous n'en avez pas
                'rameaumambu1@gmail.com',  # Remplacez par l'adresse e-mail de l'expéditeur
                [self.demande_passeport.personne.email],
                fail_silently=False,
                html_message=message_html
            )



class RendezVousANR(models.Model):
    """Représente un rendez-vous avec ANR."""
    demande_passeport = models.OneToOneField(DemandePasseport, on_delete=models.CASCADE, related_name='rendez_vous_anr')
    date_programmee = models.DateTimeField()
    anr_notifie = models.BooleanField(default=False)

    def __str__(self):
        return f"Rendez-vous {self.demande_passeport.numero_demande} avec ANR"

class StatutANR(models.Model):
    """Représente l'état du rendez-vous avec ANR."""
    demande_passeport = models.OneToOneField(DemandePasseport, on_delete=models.CASCADE, related_name='statut_anr')
    rendez_vous_complet = models.BooleanField(default=False)
    date_confirmation = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Statut ANR pour {self.demande_passeport.numero_demande}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Met à jour la demande de passeport lorsque le rendez-vous ANR est confirmé
        demande = self.demande_passeport
        demande.anr_rendez_vous_complet = self.rendez_vous_complet
        demande.planifier_rendez_vous()
        demande.save()

class StatutMinistere(models.Model):
    """Représente l'état de la demande de passeport au ministère."""
    demande_passeport = models.OneToOneField(DemandePasseport, on_delete=models.CASCADE, related_name='statut_ministere')
    rendez_vous_programme = models.BooleanField(default=False)
    date_finalisation = models.DateTimeField(blank=True, null=True)
    passeport_livre = models.BooleanField(default=False)

    def __str__(self):
        return f"Statut Ministère pour {self.demande_passeport.numero_demande}"

class DemandeRendezVous(models.Model):
    """Représente une demande de nouveau rendez-vous après un rendez-vous manqué."""
    demande_passeport = models.OneToOneField(DemandePasseport, on_delete=models.CASCADE, related_name='demande_rendez_vous')
    raison = models.TextField()  # Pourquoi le rendez-vous initial a été manqué
    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de nouveau rendez-vous pour {self.demande_passeport.numero_demande}"
