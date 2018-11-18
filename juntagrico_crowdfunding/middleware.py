from django.contrib.auth.models import User

from django.http import HttpResponseRedirect

class FunderAccess:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        print(request.path)
        if request.path != '/logout/' and request.path[:4] != '/cf/' and request.GET.get('next') != '/cf/' and request.user.is_authenticated and not hasattr(request.user, 'member'):
            return HttpResponseRedirect('/cf/')
