from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile


class EmailOrPhoneOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')

        if username is None or password is None:
            return None

        user = None

        # Tentar por username ou email
        try:
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            user = None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()

        # Se não encontrou, tentar por telefone
        if user is None:
            try:
                profile = UserProfile.objects.get(phone=username)
                user = profile.user
            except UserProfile.DoesNotExist:
                return None
            except UserProfile.MultipleObjectsReturned:
                profile = UserProfile.objects.filter(phone=username).first()
                user = profile.user if profile else None

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None