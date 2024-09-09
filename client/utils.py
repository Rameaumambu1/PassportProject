
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def envoyer_notification_email(destinataire, sujet, template_name, context):
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        sujet,
        text_content,
        settings.EMAIL_HOST_USER,
        [destinataire]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
