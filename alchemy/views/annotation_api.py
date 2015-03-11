import json
import traceback, sys
from django.views.generic import View
from django_annotation.models import *
from django_annotation.utils.transform import Document2Annotation
from django.http import JsonResponse
from django.db import transaction
from .collection_api import CollectionAPI
from .entity_category_api import EntityCategoryAPI
from .relation_category_api import RelationCategoryAPI
from .argument_role_api import ArgumentRoleAPI

class AnnotationAPI(View):
    view_name = 'annotation_api'

    @staticmethod
    def save_entity_property(entity, property):
        if not isinstance(property, dict):
            return
        for label, value in property.items():
            if isinstance(value, list):
                for val in value:
                    ep = EntityProperty(entity=entity, label=label, value=val)
                    ep.save()
            elif isinstance(value, str):
                ep = EntityProperty(entity=entity, label=label, value=value)
                ep.save()

    @staticmethod
    def save_relation_property(relation, property):
        if not isinstance(property, dict):
            return
        for label, value in property.items():
            if isinstance(value, list):
                for val in value:
                    rp = RelationProperty(relation=relation, label=label, value=val)
                    rp.save()
            elif isinstance(value, str):
                rp = RelationProperty(relation=relation, label=label, value=value)
                rp.save()
                
    @staticmethod
    @transaction.atomic
    def save_annotation(annotations, entity_category_map, relation_category_map, role_category_map, msgs):
        doc_id_count = 0

        for annotation in annotations:
            doc_id = annotation.get('doc_id')
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

                    property = entity.get('property')
                    AnnotationAPI.save_entity_property(db_entity, property)
                    
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
                    property = relation.get('property')
                    AnnotationAPI.save_relation_property(db_relation, property)
                    
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
            collection = request.POST.get('collection')
            username = request.POST.get('username')
            password = request.POST.get('password')

            entity_categories = json.loads(request.POST.get('entity_category_set'))
            relation_categories = json.loads(request.POST.get('relation_category_set'))
            
            if entity_categories is None:
                entity_categories = ()
            if relation_categories is None:
                relation_categories = ()
            
            try:
                db_user = User.objects.get(username=username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return JsonResponse({'success': False, 'message': 'user auth error'})

            msgs = []
            db_collection = CollectionAPI.get_collection(collection, db_user)
            entity_category_map = {}
            relation_category_map = {}
            role_category_map = {}

            # get entity categories
            for ent_cat in entity_categories:
                db_entity_category = EntityCategoryAPI.get_entity_category(ent_cat, db_collection)
                entity_category_map[ent_cat] = db_entity_category

            # get relation categories
            # rel_cat is <relation, roles> tuple, e.g., <Phosphorylation, <Kinase, Substrate, Site>>
            for rel_cat in relation_categories:
                db_relation_category = RelationCategoryAPI.get_relation_category(rel_cat[0], db_collection)
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