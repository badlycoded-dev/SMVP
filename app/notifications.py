from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def notify(recipient, category, title, body='', url=''):
    """Create an in-app notification, and email it too if the user opted in."""
    notification = Notification.objects.create(
        recipient=recipient, category=category, title=title, body=body, url=url,
    )

    profile = getattr(recipient, 'profile', None)
    if profile and getattr(profile, 'email_notifications', False) and recipient.email:
        try:
            send_mail(
                subject=title,
                message=body or title,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True,
            )
        except Exception:
            pass

    return notification
