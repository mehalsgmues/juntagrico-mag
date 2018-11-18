from django.contrib.auth.models import User

from juntagrico.models import Member
from juntagrico_crowdfunding.models import Funder

class AuthenticateWithEmail(object):
    @staticmethod
    def authenticate(request, username=None, password=None):
        
        try:
            user = Member.objects.get(email__iexact=username).user
            if user.check_password(password) and not user.member.inactive:
                return user
        except Member.DoesNotExist:
            # funder login, only on crowdfunding subpages
            if request.path[:4] == '/cf/' or request.GET['next'] == '/cf/':
                user = Funder.objects.get(email__iexact=username).user
                if user.check_password(password):
                    return user

            return None

    @staticmethod
    def get_user(user_id):

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
