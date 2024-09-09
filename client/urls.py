from . import views
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
# app_name = 'client' (probleme url) 



# urlpatterns = [
#     path('', views.home, name='home'),
#     path('signIn/', views.connexion, name='connexion'),
#     path('demande/', views.demande, name='demande'),
#     # Ajoutez ici d'autres patterns d'URL
# ]

urlpatterns = [
    path('', views.home, name='home'),
    path('verifier_statut/', views.verifier_statut, name='verifier_statut'),

    path('demande/<int:demande_id>/', views.demande_detail, name='demande_detail'),
    path('demande_create/', views.demande_create, name='demande_create_new'),
    path('demande_create/<int:personne_id>/', views.demande_create, name='demande_create'),

    path('personne_create/', views.personne_create, name='personne_create'),
    
    # path('demande/create/', views.demande_passeport_create, name='demande_passeport_create'),
    # path('demande/<int:demande_id>/', views.demande_passeport_detail, name='demande_detail'),
    path('demandes/', views.demande_list, name='demande_list'),  # Assurez-vous que cette ligne est présente
    path('paiement/<int:demande_id>/', views.paiement_view, name='paiement_view'),
    path('statut/anr/<int:demande_id>/', views.statut_anr_view, name='statut_anr_view'),
    path('statut/ministere/<int:demande_id>/', views.statut_ministere_view, name='statut_ministere_view'),
    path('demande/create/<int:personne_id>/', views.demande_create, name='demande_create_avec_personne'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
