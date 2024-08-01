from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Personne(models.Model):
    """Représente une personne pour laquelle une demande de passeport peut être faite."""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.TextField()

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
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE, null=True, blank=True)
    est_pour_moi = models.BooleanField(default=True)
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
        if self.est_pour_moi:
            return f"Demande {self.numero_demande} pour {self.utilisateur.username}"
        else:
            return f"Demande {self.numero_demande} pour {self.personne.prenom} {self.personne.nom}"

    def planifier_rendez_vous(self):
        """Planifie automatiquement les rendez-vous après la validation du paiement si le rendez-vous ANR a été confirmé."""
        if self.date_paiement and not self.date_rendez_vous_anr:
            # Planifie le rendez-vous avec ANR deux jours après la validation du paiement
            self.date_rendez_vous_anr = self.date_paiement + timedelta(days=2)
            self.save()

        if self.date_rendez_vous_anr and not self.date_rendez_vous_ministere and self.anr_rendez_vous_complet:
            # Planifie le rendez-vous avec le ministère deux jours après le rendez-vous ANR
            self.date_rendez_vous_ministere = self.date_rendez_vous_anr + timedelta(days=2)
            self.save()

    def verifier_rendez_vous_anr(self):
        """Vérifie automatiquement si le rendez-vous ANR est raté."""
        if self.date_rendez_vous_anr:
            date_limite = self.date_rendez_vous_anr + timedelta(days=1)
            if timezone.now() > date_limite and not self.anr_rendez_vous_complet:
                self.statut = 'annulee'
                self.save()

class Paiement(models.Model):
    """Représente le paiement pour une demande de passeport."""
    demande_passeport = models.OneToOneField(DemandePasseport, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Paiement pour {self.demande_passeport.numero_demande}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Planifie les rendez-vous lorsque le paiement est validé
        self.demande_passeport.planifier_rendez_vous()
        self.demande_passeport.save()

class RendezVousANR(models.Model):
    """Représente un rendez-vous avec la société ANR."""
    demande_passeport = models.OneToOneField(DemandePasseport, on_delete=models.CASCADE, related_name='rendez_vous_anr')
    date_programmee = models.DateTimeField()
    anr_notifie = models.BooleanField(default=False)

    def __str__(self):
        return f"Rendez-vous {self.demande_passeport.numero_demande} avec ANR"

class StatutANR(models.Model):
    """Représente l'état du rendez-vous avec la société ANR."""
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
