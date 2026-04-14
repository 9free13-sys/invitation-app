from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Invitation


@login_required
def my_invitations(request):
    user_email = (request.user.email or '').strip().lower()
    status_filter = request.GET.get('status', '').strip()

    invitations = (
        Invitation.objects
        .filter(guest__email__iexact=user_email)
        .select_related('event', 'guest')
        .order_by('-sent_at')
    )

    if status_filter in ['pending', 'accepted', 'declined']:
        invitations = invitations.filter(status=status_filter)

    total_count = Invitation.objects.filter(
        guest__email__iexact=user_email
    ).count()

    pending_count = Invitation.objects.filter(
        guest__email__iexact=user_email,
        status='pending'
    ).count()

    accepted_count = Invitation.objects.filter(
        guest__email__iexact=user_email,
        status='accepted'
    ).count()

    declined_count = Invitation.objects.filter(
        guest__email__iexact=user_email,
        status='declined'
    ).count()

    return render(request, 'invitations/my_invitations.html', {
        'invitations': invitations,
        'status_filter': status_filter,
        'total_count': total_count,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'declined_count': declined_count,
    })