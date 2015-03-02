from django.views.generic import View
from django_annotation.models import *
from django.core import serializers
from django.http import JsonResponse
from alchemy.utils.document_retriever import DocumentRetriever
import json

# Create your views here.

class UserAPI(View):
    view_name = 'user_api'

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            msg = serializers.serialize('json', user)
        except User.DoesNotExist:
            msg = JsonResponse({'success': False, 'message': 'user not exists'})
        except  User.MultipleObjectsReturned:
            msg = JsonResponse({'success': False, 'message': 'multiple records found'})

        return msg

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username is None or password is None:
            msg = {'success': False, 'message': 'username or password is null'}
        else:
            try:
                user = User.objects.get(username=username)
                msg = {'success': False, 'message': 'user exists'}
            except User.DoesNotExist:
                user = User(username=username, password=password)
                user.save()
                msg = {'success': True}
            except User.MultipleObjectsReturned:
                msg = {'success': False, 'message': 'user exists'}

        return JsonResponse(msg)


class VersionAPI(View):
    view_name = 'version_api'

    def get(self, request, username, version):
        try:
            version = Version.objects.get(version=version, user__username=username)
            return JsonResponse({'success': True})
        except Version.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'version not exists'})
        except Version.MultipleObjectsReturned:
            return JsonResponse({'success': False, 'message': 'multiple records found'})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        version = request.POST.get('version')

        if username is None or password is None or version is None:
            msg = {'success': False, 'message': 'one of the fields is null'}
        else:
            try:
                user = User.objects.get(username=username, password=password)

            except (User.DoesNotExist, User.MultipleObjectsReturned):
                msg = {'success': False, 'message': 'user not exists'}
            else:
                try:
                    version = Version.objects.get(user=user)
                    msg = {'success': False, 'message': 'version exists'}
                except Version.DoesNotExist:
                    version = Version(user=user, version=version)
                    version.save()
                    msg = {'success': True}

        return JsonResponse(msg)


class DocumentAPI(View):
    view_name = 'document_api'

    def post(self, request):
        documents = request.POST.get('documents')
        try:
            pmid_list = json.loads(documents)
            medlines = DocumentRetriever.retrieve(pmid_list)
            return JsonResponse(medlines, safe=False)
        except:
            return JsonResponse({'success': False})

    def get(self, request, pmid):
        medlines = DocumentRetriever.retrieve([pmid])
        return JsonResponse(medlines, safe=False)


class AnnotationAPI(View):
    view_name = 'annotation_api'

    def get(self):
        pass

    def post(self, request):
        annotations = request.POST.get('annotations')

        pass