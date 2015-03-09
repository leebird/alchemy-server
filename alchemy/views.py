from django.views.generic import View
from django_annotation.models import *
from django_annotation.utils.transform import Document2Annotation
from django.core import serializers
from django.http import JsonResponse
from alchemy.utils.document_retriever import DocumentRetriever
import json
import traceback, sys
from django.db import transaction

# Create your views here.

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


class VersionAPI(View):
    view_name = 'version_api'

    def get(self, request, username, version):
        user = UserAPI.get_user(username, auth=False)
        db_version = VersionAPI.get_version(version, user)
        if db_version:
            return JsonResponse({'version': version.version, 'username': username})
        else:
            return JsonResponse({'success': False})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        version = request.POST.get('version')

        db_version = self.save_version(version, username, password)

        if db_version:
            return JsonResponse({'success': True, 'version': db_version.version, 'username': username})
        else:
            return JsonResponse({'success': False})

    @classmethod
    def get_version(cls, version, user):
        if version is None or len(version) == '':
            return None
        try:
            db_version = Version.objects.get(user=user, version=version)
            return db_version
        except (Version.DoesNotExist, Version.MultipleObjectsReturned):
            return None

    @classmethod
    def save_version(cls, version, username, password):
        if version is None or len(version) == 0:
            return None
        else:
            user = UserAPI.get_user(username=username, password=password, auth=True)
            if user:
                db_version = VersionAPI.get_version(user=user, version=version)
                if db_version:
                    return db_version
                else:
                    db_version = Version(user=user, version=version)
                    db_version.save()
                    return db_version


class DocumentAPI(View):
    view_name = 'document_api'

    def post(self, request):
        documents = request.POST.get('document_set')
        try:
            pmid_list = set(json.loads(documents))
            doc_text = DocumentRetriever.retrieve(pmid_list)
            return JsonResponse(doc_text)
        except:
            traceback.print_exc(file=sys.stderr)
            return JsonResponse({'success': False})

    def get(self, request, pmid):
        medlines = DocumentRetriever.retrieve({pmid})
        return JsonResponse(medlines, safe=False)

    @classmethod
    def get_document(cls, doc_id):
        try:
            document = Document.objects.get(doc_id=doc_id)
            return document
        except (Document.DoesNotExist, Document.MultipleObjectsReturned):
            return None

    @classmethod
    def save_document(cls, doc_id, text):
        document = cls.get_document(doc_id)
        if document:
            return document
        else:
            doc = Document(doc_id=doc_id, text=text)
            doc.save()
            return doc


class EntityCategoryAPI(View):
    view_name = 'entity_category_api'

    def get(self, request, entity_category):
        pass

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        version = request.POST.get('version')
        entity_categories = json.loads(request.POST.get('entity_category_set'))
        db_user = UserAPI.get_user(username, password, auth=True)
        db_version = VersionAPI.get_version(version, db_user)

        if (not db_user) or (not db_version):
            return JsonResponse({'success': False})

        for ent_cat in entity_categories:
            self.save_entity_category(ent_cat, db_version)

        return JsonResponse({'success': True})

    @classmethod
    def get_entity_category(cls, entity_category, db_version):

        try:
            db_category = EntityCategory.objects.get(category=entity_category, version=db_version)
        except (EntityCategory.DoesNotExist, EntityCategory.MultipleObjectsReturned):
            return False
        else:
            return db_category

    @classmethod
    def save_entity_category(cls, entity_category, db_version):
        if len(entity_category) == 0:
            return False

        db_category = cls.get_entity_category(entity_category=entity_category, db_version=db_version)
        if db_category:
            return db_category
        else:
            db_category = EntityCategory(category=entity_category, version=db_version)
            db_category.save()
            return db_category


class RelationCategoryAPI(View):
    view_name = 'relation_category_api'

    def get(self, relation_category):
        pass

    def post(self, request):
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            version = request.POST.get('version')
            relation_categories = json.loads(request.POST.get('relation_category_set'))

            db_user = UserAPI.get_user(username, password, auth=True)
            db_version = VersionAPI.get_version(version, db_user)

            if (not db_user) or (not db_version):
                return JsonResponse({'success': False})

            for rel_cat, roles in relation_categories:
                db_category = self.save_relation_category(rel_cat, db_version)
                for role in roles:
                    ArgumentRoleAPI.save_argument_role(role, db_category)

            return JsonResponse({'success': True})
        except:
            traceback.print_exc(file=sys.stderr)

    @classmethod
    def get_relation_category(cls, relation_category, db_version):
        try:
            db_category = RelationCategory.objects.get(category=relation_category, version=db_version)
        except(RelationCategory.DoesNotExist, RelationCategory.MultipleObjectsReturned):
            return None
        else:
            return db_category

    @classmethod
    def save_relation_category(cls, relation_category, db_version):
        if relation_category is None or len(relation_category) == 0:
            return None

        db_category = cls.get_relation_category(relation_category=relation_category, db_version=db_version)
        if db_category:
            return db_category
        else:
            db_category = RelationCategory(category=relation_category, version=db_version)
            db_category.save()
            return db_category


class ArgumentRoleAPI(View):
    view_name = 'argument_role_api'

    def get(self, request, argument_role):
        pass

    def post(self, request):
        pass

    @classmethod
    def get_argument_role(cls, role, relation_category):
        try:
            db_role = ArgumentRole.objects.get(role=role, relation_category=relation_category)
        except(ArgumentRole.DoesNotExist, ArgumentRole.MultipleObjectsReturned):
            return False
        else:
            return db_role

    @classmethod
    def save_argument_role(cls, role, relation_category):
        if len(role) == 0:
            return False

        db_role = cls.get_argument_role(role, relation_category)
        if db_role:
            return db_role
        else:
            db_role = ArgumentRole(role=role, relation_category=relation_category)
            db_role.save()
            return db_role


class AnnotationAPI(View):
    view_name = 'annotation_api'

    @staticmethod
    @transaction.atomic
    def save_annotation(annotations, entity_category_map, relation_category_map, role_category_map, msgs):
        doc_id_count = 0

        for doc_id, annotation in annotations.items():
            try:
                doc = Document.objects.get(doc_id=doc_id)
            except (Document.DoesNotExist, Document.MultipleObjectsReturned):
                msgs.append('document not exists or multiple found: ')
                continue
            else:
                id_map = {}

                for entity in annotation.get('entity_set'):
                    category = entity.get('category')
                    db_category = entity_category_map.get(category)
                    if db_category is None:
                        msgs.append('entity category not found: ' + doc_id + ' ' + category)
                        continue

                    start = entity.get('start')
                    end = entity.get('end')
                    text = entity.get('text')
                    id_ = entity.get('id')
                    db_entity = Entity(doc=doc, category=db_category, start=start, end=end, text=text, uid=id_)
                    db_entity.save()
                    id_map[id_] = db_entity

                for relation in annotation.get('relation_set'):
                    category = relation.get('category')
                    db_category = relation_category_map.get(category)
                    if db_category is None:
                        msgs.append('relation category not found: ' + doc_id + ' ' + category)
                        continue
                    id_ = relation.get('id')

                    db_relation = Relation(doc=doc, category=db_category, uid=id_)
                    db_relation.save()
                    id_map[id_] = db_relation

                for relation in annotation.get('relation_set'):
                    id_ = relation.get('id')
                    category = relation.get('category')
                    for arg_role, arg_id in relation.get('argument_set'):
                        argument = id_map.get(arg_id)
                        db_role = role_category_map.get((category, arg_role))
                        db_relation = id_map.get(id_)

                        if db_role is None:
                            msgs.append('role not found: ' + doc_id + ' ' + str((category, arg_role)))
                            continue
                        
                        if argument is not None:
                            if isinstance(argument, Entity):
                                arg_entity = EntityAsArgument(role=db_role, argument=argument, relation=db_relation)
                                arg_entity.save()
                            elif isinstance(argument, Relation):
                                arg_relation = RelationAsArgument(role=db_role, argument=argument, relation=db_relation)
                                arg_relation.save()

                doc_id_count += 1
        return msgs, doc_id_count

    def get(self, request, pmid):
        documents = Document.objects.filter(doc_id=pmid)
        transformer = Document2Annotation(documents)
        annotations = transformer.transform()
        return JsonResponse(annotations)

    @transaction.atomic
    def post(self, request):
        try:
            annotations_json = request.POST.get('annotation_set')
            annotations = json.loads(annotations_json)
            version = request.POST.get('version')
            username = request.POST.get('username')
            password = request.POST.get('password')

            entity_categories = json.loads(request.POST.get('entity_category_set'))
            relation_categories = json.loads(request.POST.get('relation_category_set'))

            try:
                db_user = User.objects.get(username=username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return JsonResponse({'success': False, 'message': 'user auth error'})

            msgs = []
            db_version = VersionAPI.get_version(version, db_user)
            entity_category_map = {}
            relation_category_map = {}
            role_category_map = {}

            # get entity categories
            for ent_cat in entity_categories:
                db_entity_category = EntityCategoryAPI.get_entity_category(ent_cat, db_version)
                entity_category_map[ent_cat] = db_entity_category

            # get relation categories
            # rel_cat is <relation, roles> tuple, e.g., <Phosphorylation, <Kinase, Substrate, Site>>
            for rel_cat in relation_categories:
                db_relation_category = RelationCategoryAPI.get_relation_category(rel_cat[0], db_version)
                relation_category_map[rel_cat[0]] = db_relation_category

            # get argument roles
            for rel_cat in relation_categories:
                roles = rel_cat[1]
                db_relation_category = relation_category_map[rel_cat[0]]
                for role in roles:
                    db_role = ArgumentRoleAPI.get_argument_role(role, db_relation_category)
                    # map from <phosphorylation, Substrate> to db_role
                    role_category_map[(rel_cat[0], role)] = db_role

            msgs, doc_id_count = self.save_annotation(annotations, entity_category_map,
                                                      relation_category_map, role_category_map, msgs)

            return JsonResponse({'message': msgs, 'imported_doc': doc_id_count})
        except Exception:
            traceback.print_exc(file=sys.stderr)