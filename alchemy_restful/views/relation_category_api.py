from django.views.generic import View
from alchemy_server.models import *
from django.http import JsonResponse
import json
import traceback, sys
from .user_api import UserAPI
from .collection_api import CollectionAPI
from .argument_role_api import ArgumentRoleAPI


class RelationCategoryAPI(View):
    view_name = 'relation_category_api'

    def get(self, relation_category):
        pass

    def post(self, request):
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            collection = request.POST.get('collection')
            relation_categories = json.loads(request.POST.get('relation_category_set'))
            if relation_categories is None:
                return JsonResponse({'success': True})
            
            db_user = UserAPI.get_user(username, password, auth=True)
            db_collection = CollectionAPI.get_collection(collection, db_user)

            if (not db_user) or (not db_collection):
                return JsonResponse({'success': False})

            for rel_cat, roles in relation_categories:
                db_category = self.save_relation_category(rel_cat, db_collection)
                for role in roles:
                    ArgumentRoleAPI.save_argument_role(role, db_category)

            return JsonResponse({'success': True})
        except:
            traceback.print_exc(file=sys.stderr)

    @classmethod
    def get_relation_category(cls, relation_category, db_collection):
        try:
            db_category = RelationCategory.objects.get(category=relation_category, collection=db_collection)
        except(RelationCategory.DoesNotExist, RelationCategory.MultipleObjectsReturned):
            return None
        else:
            return db_category

    @classmethod
    def save_relation_category(cls, relation_category, db_collection):
        if relation_category is None or len(relation_category) == 0:
            return None

        db_category = cls.get_relation_category(relation_category=relation_category, db_collection=db_collection)
        if db_category:
            return db_category
        else:
            db_category = RelationCategory(category=relation_category, collection=db_collection)
            db_category.save()
            return db_category