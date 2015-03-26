from django.views.generic import View
from alchemy_server.models import *
from django.http import JsonResponse
from .user_api import UserAPI


class CollectionAPI(View):
    view_name = 'collection_api'

    def get(self, request, username, collection):
        user = UserAPI.get_user(username, auth=False)
        db_collection = CollectionAPI.get_collection(collection, user)
        if db_collection:
            return JsonResponse({'collection': collection.collection, 'username': username})
        else:
            return JsonResponse({'success': False})

    def post(self, request):
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            collection = request.POST.get('collection')

            db_collection = self.save_collection(collection, username, password)

            if db_collection:
                return JsonResponse({'success': True, 'collection': db_collection.collection, 'username': username})
            else:
                return JsonResponse({'success': False})
        except Exception as e:
            print(e)

    @classmethod
    def get_collection_docs(cls, collection):

        entity_category = EntityCategory.objects.filter(collection=collection)
        relation_category = RelationCategory.objects.filter(collection=collection)
        entities = Entity.objects.only('doc').filter(
            category__in=entity_category).values('doc_id')
        relations = Relation.objects.only('doc').filter(
            category__in=relation_category).values('doc_id')

        docs = set()
        for entity in entities:
            docs.add(entity.get('doc_id'))
        for relation in relations:
            docs.add(relation.get('doc_id'))
            
        # this is doc.id, not doc.doc_id
        return docs

    @classmethod
    def get_collection(cls, collection, user):
        if collection is None or len(collection) == '':
            return None
        try:
            db_category = Collection.objects.get(user=user, collection=collection)
            return db_category
        except (Collection.DoesNotExist, Collection.MultipleObjectsReturned):
            return None

    @classmethod
    def save_collection(cls, collection, username, password):
        if collection is None or len(collection) == 0:
            return None
        else:
            user = UserAPI.get_user(username=username, password=password, auth=True)
            if user:
                db_collection = CollectionAPI.get_collection(user=user, collection=collection)
                if db_collection:
                    return db_collection
                else:
                    db_collection = Collection(user=user, collection=collection)
                    db_collection.save()
                    return db_collection