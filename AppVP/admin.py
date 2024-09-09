# AppVP/admin.py

from django.contrib import admin
from .models import Universite, Faculte, Departement, Promotion, Cours, Horaire, Examen, Interrogation, TravailPratique, Etudiant
from django.contrib.auth.admin import UserAdmin




class UniversiteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse')
    search_fields = ('nom',)

class FaculteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'universite')
    list_filter = ('universite',)
    search_fields = ('nom', 'description')

class DepartementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'faculte')
    list_filter = ('faculte',)
    search_fields = ('nom',)

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'departement', 'annee_debut', 'annee_fin', 'numero')
    list_filter = ('departement', 'annee_debut', 'annee_fin')
    search_fields = ('nom', 'numero')

class CoursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'promotion')
    list_filter = ('promotion',)
    search_fields = ('nom', 'code')

class HoraireAdmin(admin.ModelAdmin):
    list_display = ('cours', 'jour_de_la_semaine', 'periode', 'heure_debut', 'heure_fin', 'salle')
    list_filter = ('cours', 'periode', 'jour_de_la_semaine')
    search_fields = ('cours__nom', 'salle')

class ExamenAdmin(admin.ModelAdmin):
    list_display = ('cours', 'date', 'heure', 'duree', 'salle')
    list_filter = ('cours', 'date')
    search_fields = ('cours__nom', 'salle')

class InterrogationAdmin(admin.ModelAdmin):
    list_display = ('cours', 'date', 'heure', 'duree', 'salle')
    list_filter = ('cours', 'date')
    search_fields = ('cours__nom', 'salle')

class TravailPratiqueAdmin(admin.ModelAdmin):
    list_display = ('cours', 'date_depot', 'description')
    list_filter = ('cours', 'date_depot')
    search_fields = ('cours__nom', 'description')

# class EtudiantAdmin(UserAdmin):
#     list_display = ('username', 'numero_promotion', 'is_staff', 'is_active')
#     search_fields = ('username', 'numero_promotion')
class EtudiantAdmin(UserAdmin):
    model = Etudiant
    list_display = ('username', 'nom', 'postnom', 'prenom', 'numero_promotion', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'nom', 'postnom', 'prenom', 'numero_promotion')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'postnom', 'prenom', 'numero_promotion')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nom', 'postnom', 'prenom', 'numero_promotion', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )


admin.site.register(Universite, UniversiteAdmin)
admin.site.register(Faculte, FaculteAdmin)
admin.site.register(Departement, DepartementAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Horaire, HoraireAdmin)
admin.site.register(Examen, ExamenAdmin)
admin.site.register(Interrogation, InterrogationAdmin)
admin.site.register(TravailPratique, TravailPratiqueAdmin)
admin.site.register(Etudiant, EtudiantAdmin)
