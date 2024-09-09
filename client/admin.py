from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Personne, DemandePasseport, Paiement, RendezVousANR, StatutANR, StatutMinistere, DemandeRendezVous

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'date_naissance', 'email')
    search_fields = ('prenom', 'nom', 'email')
    list_filter = ('date_naissance',)
    ordering = ('-date_naissance',)

@admin.register(DemandePasseport)
class DemandePasseportAdmin(admin.ModelAdmin):
    list_display = ('numero_demande', 'personne', 'statut', 'date_demande', 'date_paiement', 'date_rendez_vous_anr', 'date_rendez_vous_ministere')
    search_fields = ('numero_demande', 'personne__prenom', 'personne__nom')
    list_filter = ('statut', 'date_demande')
    readonly_fields = ('numero_demande', 'date_demande', 'date_paiement', 'date_revision', 'date_finalisation', 'date_rejet', 'date_rendez_vous_anr', 'date_rendez_vous_ministere')

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('demande_passeport', 'montant', 'date_paiement')
    search_fields = ('demande_passeport__numero_demande',)
    readonly_fields = ('date_paiement',)

@admin.register(RendezVousANR)
class RendezVousANRAdmin(admin.ModelAdmin):
    list_display = ('demande_passeport', 'date_programmee', 'anr_notifie')
    search_fields = ('demande_passeport__numero_demande',)
    readonly_fields = ('date_programmee', 'anr_notifie')

@admin.register(StatutANR)
class StatutANRAdmin(admin.ModelAdmin):
    list_display = ('demande_passeport', 'rendez_vous_complet', 'date_confirmation')
    search_fields = ('demande_passeport__numero_demande',)
    readonly_fields = ('date_confirmation',)

@admin.register(StatutMinistere)
class StatutMinistereAdmin(admin.ModelAdmin):
    list_display = ('demande_passeport', 'rendez_vous_programme', 'date_finalisation', 'passeport_livre')
    search_fields = ('demande_passeport__numero_demande',)
    readonly_fields = ('date_finalisation',)

@admin.register(DemandeRendezVous)
class DemandeRendezVousAdmin(admin.ModelAdmin):
    list_display = ('demande_passeport', 'raison', 'date_demande')
    search_fields = ('demande_passeport__numero_demande', 'raison')
    readonly_fields = ('date_demande',)
