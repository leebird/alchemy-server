from django.views.generic import View
from django_annotation.models import *
from django.http import JsonResponse
import json
from .user_api import UserAPI
from .collection_api import CollectionAPI


class EntityCategoryAPI(View):
    view_name = 'entity_category_api'

    def get(self, request, entity_category):
        pass

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        collection = request.POST.get('collection')
        entity_categories = json.loads(request.POST.get('entity_category_set'))
        db_user = UserAPI.get_user(username, password, auth=True)
        db_collection = CollectionAPI.get_collection(collection, db_user)

        if (not db_user) or (not db_collection):
            return JsonResponse({'success': False})

        for ent_cat in entity_categories:
            self.save_entity_category(ent_cat, db_collection)

        return JsonResponse({'success': True})

    @classmethod
    def get_entity_category(cls, entity_category, db_collection):

        try:
            db_category = EntityCategory.objects.get(category=entity_category, collection=db_collection)
        except (EntityCategory.DoesNotExist, EntityCategory.MultipleObjectsReturned):
            return False
        else:
            return db_category

    @classmethod
    def save_entity_category(cls, entity_category, db_collection):
        if len(entity_category) == 0:
            return False

        db_category = cls.get_entity_category(entity_category=entity_category, db_collection=db_collection)
        if db_category:
            return db_category
        else:
            db_category = EntityCategory(category=entity_category, collection=db_collection)
            db_category.save()
            return db_category
