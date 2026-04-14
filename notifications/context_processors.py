from .models import Notification


def notification_count(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')

        unread_count = notifications.filter(is_read=False).count()
    else:
        notifications = Notification.objects.none()
        unread_count = 0

    return {
        'unread_notifications_count': unread_count,
        'notifications': notifications,
    }