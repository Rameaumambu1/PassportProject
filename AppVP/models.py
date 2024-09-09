from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class Universite(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.TextField()

    def __str__(self):
        return self.nom

class Faculte(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    universite = models.ForeignKey(Universite, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

class Departement(models.Model):
    nom = models.CharField(max_length=255)
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

class Promotion(models.Model):
    nom = models.CharField(max_length=255)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    annee_debut = models.PositiveIntegerField()
    annee_fin = models.PositiveIntegerField()
    numero = models.CharField(max_length=14, unique=True)

    def clean(self):
        if len(self.numero) != 14:
            raise ValidationError("Le numéro de la promotion doit comporter exactement 14 caractères.")
        if self.annee_debut > self.annee_fin:
            raise ValidationError("L'année de début doit être antérieure à l'année de fin.")

    def save(self, *args, **kwargs):
        self.clean()  # Assurer que la validation est appelée avant de sauvegarder
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nom} ({self.numero}) - {self.annee_debut}-{self.annee_fin}'

class Cours(models.Model):
    nom = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.code} - {self.nom}'

class Horaire(models.Model):
    PERIOD_CHOICES = [
        ('AM', 'Avant-midi'),
        ('PM', 'Après-midi'),
    ]

    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    jour_de_la_semaine = models.CharField(max_length=9)  # e.g., 'Lundi'
    periode = models.CharField(max_length=2, choices=PERIOD_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    salle = models.CharField(max_length=10)

    class Meta:
        unique_together = ('cours', 'jour_de_la_semaine', 'periode', 'salle')
        verbose_name = "Horaire"
        verbose_name_plural = "Horaires"

    def save(self, *args, **kwargs):
        if self.periode == 'AM':
            self.heure_debut = '08:30:00'
            self.heure_fin = '12:30:00'
        elif self.periode == 'PM':
            self.heure_debut = '14:00:00'
            self.heure_fin = '18:00:00'
        super().save(*args, **kwargs)

    def clean(self):
        if self.periode == 'AM':
            if not (self.heure_debut == '08:30:00' and self.heure_fin == '12:30:00'):
                raise ValidationError("Les horaires pour l'avant-midi doivent être de 08:30 à 12:30.")
        elif self.periode == 'PM':
            if not (self.heure_debut == '14:00:00' and self.heure_fin == '18:00:00'):
                raise ValidationError("Les horaires pour l'après-midi doivent être de 14:00 à 18:00.")
        super().clean()

    def __str__(self):
        periode_str = 'Avant-midi' if self.periode == 'AM' else 'Après-midi'
        return f'{self.cours.nom} - {self.jour_de_la_semaine} ({periode_str}) de {self.heure_debut} à {self.heure_fin}'

class Examen(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date = models.DateField()
    heure = models.TimeField()
    duree = models.DurationField()  # e.g., 1 heure 30 minutes
    salle = models.CharField(max_length=10)

    def __str__(self):
        return f'Examen pour {self.cours.nom} le {self.date} à {self.heure}'

class Interrogation(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date = models.DateField()
    heure = models.TimeField()
    duree = models.DurationField()
    salle = models.CharField(max_length=10)

    def __str__(self):
        return f'Interrogation pour {self.cours.nom} le {self.date} à {self.heure}'

class TravailPratique(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_depot = models.DateField()  # Date limite pour déposer le travail
    description = models.TextField()  # Description du travail pratique

    def __str__(self):
        return f'Travail Pratique pour {self.cours.nom} à déposer le {self.date_depot}'


    





from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models



class EtudiantManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, password, **extra_fields)



class Etudiant(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    nom = models.CharField(max_length=150)
    postnom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    numero_promotion = models.CharField(max_length=14)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nom', 'postnom', 'prenom', 'numero_promotion']

    objects = EtudiantManager()  # Use your custom manager here

    def __str__(self):
        return self.username

    # def get_promotions_courses(self):
    #     return self.promotion.cours.all()

    def get_horaires(self):
        return Horaire.objects.filter(cours__in=self.get_promotions_courses())

    def get_examens(self):
        return Examen.objects.filter(cours__in=self.get_promotions_courses())

    def get_interrogations(self):
        return Interrogation.objects.filter(cours__in=self.get_promotions_courses())

    def get_travaux_pratiques(self):
        return TravailPratique.objects.filter(cours__in=self.get_promotions_courses())




