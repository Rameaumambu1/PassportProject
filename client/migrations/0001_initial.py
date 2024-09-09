# Generated by Django 5.0.4 on 2024-08-04 15:27

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Personne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField()),
                ('adresse', models.TextField()),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='DemandePasseport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('est_pour_moi', models.BooleanField(default=True)),
                ('numero_demande', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('payee', 'Payée'), ('en_revision', 'En révision'), ('terminee', 'Terminée'), ('rejettee', 'Rejetée'), ('annulee', 'Annulée')], default='en_attente', max_length=20)),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('date_paiement', models.DateTimeField(blank=True, null=True)),
                ('date_revision', models.DateTimeField(blank=True, null=True)),
                ('date_finalisation', models.DateTimeField(blank=True, null=True)),
                ('date_rejet', models.DateTimeField(blank=True, null=True)),
                ('date_rendez_vous_anr', models.DateTimeField(blank=True, null=True)),
                ('date_rendez_vous_ministere', models.DateTimeField(blank=True, null=True)),
                ('anr_rendez_vous_complet', models.BooleanField(default=False)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('personne', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='client.personne')),
            ],
        ),
        migrations.CreateModel(
            name='DemandeRendezVous',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raison', models.TextField()),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('demande_passeport', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='demande_rendez_vous', to='client.demandepasseport')),
            ],
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_paiement', models.DateTimeField(default=django.utils.timezone.now)),
                ('demande_passeport', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paiement', to='client.demandepasseport')),
            ],
        ),
        migrations.CreateModel(
            name='RendezVousANR',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_programmee', models.DateTimeField()),
                ('anr_notifie', models.BooleanField(default=False)),
                ('demande_passeport', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rendez_vous_anr', to='client.demandepasseport')),
            ],
        ),
        migrations.CreateModel(
            name='StatutANR',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rendez_vous_complet', models.BooleanField(default=False)),
                ('date_confirmation', models.DateTimeField(blank=True, null=True)),
                ('demande_passeport', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statut_anr', to='client.demandepasseport')),
            ],
        ),
        migrations.CreateModel(
            name='StatutMinistere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rendez_vous_programme', models.BooleanField(default=False)),
                ('date_finalisation', models.DateTimeField(blank=True, null=True)),
                ('passeport_livre', models.BooleanField(default=False)),
                ('demande_passeport', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statut_ministere', to='client.demandepasseport')),
            ],
        ),
    ]
