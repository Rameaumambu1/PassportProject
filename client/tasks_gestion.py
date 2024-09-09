# un fichier de gestion des tâches

from celery import Celery
from .tasks import envoyer_rappel_rendez_vous_anr
from datetime import timedelta

app = Celery('tasks', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
    'envoyer-rappels-rendez-vous-anr': {
        'task': 'client.tasks.envoyer_rappel_rendez_vous_anr',
        'schedule': timedelta(days=1),  # Exécuter tous les jours
    },
}
