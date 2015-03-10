from django.views.generic import View
from django_annotation.models import *
from django.http import JsonResponse

class UserAPI(View):
    view_name = 'user_api'

    def get(self, request, username):
        user = self.get_user(username, auth=False)
        if user:
            msg = {'username': user.username}
        else:
            msg = {'success': False}
        return JsonResponse(msg)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username is None or password is None or len(username) == 0:
            msg = {'success': False, 'message': 'username or password is null'}
        else:
            res = self.save_user(username, password)
            if res:
                msg = {'success': True}
            else:
                msg = {'success': False}

        return JsonResponse(msg)

    @classmethod
    def get_user(cls, username, password=None, auth=False):
        try:
            if auth:
                user = User.objects.get(username=username, password=password)
            else:
                user = User.objects.get(username=username)
            return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    @classmethod
    def save_user(cls, username, password):
        user = cls.get_user(username, auth=False)
        if user:
            return user
        else:
            user = User(username=username, password=password)
            user.save()
            return user