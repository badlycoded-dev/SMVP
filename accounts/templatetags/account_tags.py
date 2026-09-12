from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def days_on_site(date_joined):
    diff = timezone.now() - date_joined
    days = diff.days

    if days <= 0:
        return "Today"

    if days % 10 == 1 and days % 100 != 11:
        suffix = "day ago"
    elif days % 10 in [2, 3, 4] and days % 100 not in [12, 13, 14]:
        suffix = "days ago"
    else:
        suffix = "days ago"

    return f"{days} {suffix}"