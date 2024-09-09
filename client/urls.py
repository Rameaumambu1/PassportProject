from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signIn/', views.connexion, name='connexion'),
    # Ajoutez ici d'autres patterns d'URL
]
