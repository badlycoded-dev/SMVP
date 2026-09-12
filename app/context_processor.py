from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def notifications(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}
    return {'unread_notifications_count': request.user.notifications.filter(is_read=False).count()}