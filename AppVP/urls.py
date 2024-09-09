# myapp/urls.py
from django.urls import path
from .views import vue_connexion, vue_inscription
from . import views

urlpatterns = [
   
    path('accueil/', views.vue_accueil, name='accueil'),
    path('connexion/', views.vue_connexion, name='connexion'),
    path('inscription/', vue_inscription, name='inscription'),
]
