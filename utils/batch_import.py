import sys
import os
import codecs
import json

from alchemy_init import django_init
django_init()

from alchemy_server.models import *
from submodules.annotation.readers import AnnParser
from django.db import transaction


class Importer:
    """ populate database with data in a folder
    """

    def __init__(self, path):
        self.path = path
        self.entityType = {}
        self.relationType = {}
        self.argumentType = {}
        self.filename = None

    @transaction.atomic
    def populate(self):
        def event_handler(event, fields):
            if len(fields) == 0:
                return
            
            attrs = json.loads(fields[0])
            
            for attr_name, attr_value in attrs.items():
                attr_value = attr_value[0]
                print(attr_value)
                event.property.add(attr_name, attr_value)

        def relation_handler(relation, fields):
            if len(fields) == 0:
                return
            
            attrs = json.loads(fields[0])

            for attr_name, attr_value in attrs.items():
                attr_value = attr_value[0]
                relation.property.add(attr_name, attr_value)
                
        reader = AnnParser(event_handler=event_handler,relation_handler=relation_handler)
        
        for root, _, files in os.walk(self.path):
            for f in files:
                if not f.endswith('.txt'):
                    continue

                txt = codecs.open(os.path.join(root, f), 'r', 'utf-8')
                text = txt.read()
                txt.close()

                self.filename = f[:-4]
                ann = os.path.join(root, self.filename + '.ann')
                annotation = reader.parse_file(ann)

                self.process_document(text, annotation)

    def process_document(self, text, annotation):
        d = Document(doc_id=self.filename, text=text)
        d.save()

        tid2entity = {}

        if annotation is None:
            return

        self.add_entity(d, annotation.entities, tid2entity)
        self.add_relation(d, annotation.get_event_without_trigger(), tid2entity)
        self.add_event(d, annotation.get_event_with_trigger(), tid2entity)

    def add_entity(self, doc, entityList, tid2entity):
        for t in entityList:
            typing = self.get_entity_type(t.category)
            entity = Entity(doc=doc, category=typing, start=t.start, end=t.end, text=t.text)
            entity.save()
            tid2entity[t.property.get('id')] = entity

            for key, value in t.property.vault.items():
                entity.entityattribute_set.create(attribute=key, value=value)

    def add_relation(self, doc, relationList, tid2entity):
        for r in relationList:
            if r.property.get('direction') == 'G2M':
                continue
                
            typing = self.get_relation_type(r.category)
            relation = Relation(doc=doc, category=typing)
            relation.save()

            arg0 = tid2entity[r.arguments[0].value.property.get('id')]
            arg1 = tid2entity[r.arguments[1].value.property.get('id')]

            arg0Type = self.get_argument_type(relation.category, arg0.category, 'Agent')
            arg1Type = self.get_argument_type(relation.category, arg1.category, 'Theme')

            relation_arg = EntityAsArgument(category=arg0Type,
                                            relation=relation,
                                            argument=arg0)

            relation_arg.save()
            relation_arg = EntityAsArgument(category=arg1Type,
                                            relation=relation,
                                            argument=arg1)

            relation_arg.save()


    def add_event(self, doc, eventList, tid2entity):
        for e in eventList:
            print(e.property.vault)
            if e.property.get('direction') == 'G2M':
                continue
                
            typing = self.get_relation_type(e.category)
            relation = Relation(doc=doc, category=typing)
            relation.save()

            arg0 = tid2entity[e.arguments[0].value.property.get('id')]
            arg1 = tid2entity[e.arguments[1].value.property.get('id')]

            arg0Type = self.get_argument_type(relation.category, arg0.category, 'Agent')
            arg1Type = self.get_argument_type(relation.category, arg1.category, 'Theme')

            relation_arg = EntityAsArgument(category=arg0Type,
                                            relation=relation,
                                            argument=arg0)

            relation_arg.save()
            relation_arg = EntityAsArgument(category=arg1Type,
                                            relation=relation,
                                            argument=arg1)

            relation_arg.save()

            trigger = tid2entity[e.trigger.property.get('id')]
            triggerType = self.get_argument_type(relation.category, trigger.category, 'Trigger')
            relation_arg = EntityAsArgument(category=triggerType,
                                            relation=relation,
                                            argument=trigger)
            relation_arg.save()

            for key, values in e.property.vault.items():
                values = set(values)
                for value in values:
                    relation.relationattribute_set.create(attribute=key, value=value)

    def get_entity_type(self, category):
        '''
        get entity type from database or local cache
        '''
        if category in self.entityType:
            return self.entityType[category]
        typing = EntityCategory.objects.filter(category=category)

        if len(typing) == 0:
            raise KeyError('Entity type is not defined', category)

        self.entityType[category] = typing[0]
        return typing[0]

    def get_relation_type(self, category):
        '''
        get relation type from database or local cache
        '''
        if category in self.relationType:
            return self.relationType[category]
        typing = RelationCategory.objects.filter(category=category)

        if len(typing) == 0:
            raise KeyError('Relation type is not defined '+category)

        self.relationType[category] = typing[0]
        return typing[0]

    def get_argument_type(self, relationType, entityType, category):
        '''
        get argument type from database or local cache
        relation, entity and category define an argument type
        relation and category can be linked to multiple types of entities
        e.g., Target's theme could be protein or complex
        '''
        # print relationType,entityType,category
        if (relationType.category, entityType.category, category) in self.argumentType:
            return self.argumentType[(relationType.category, entityType.category, category)]
        typing = ArgumentRole.objects.filter(relation_type=relationType,
                                             entity_type=entityType,
                                             category=category)

        if len(typing) == 0:
            raise KeyError('Argument type is not defined '+relationType.category + entityType.category + category)

        self.argumentType[(relationType.category, entityType.category, category)] = typing[0]
        return typing[0]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Specify corpus path')
        sys.exit(0)
    corpus_path = sys.argv[1]
    importer = Importer(corpus_path)
    importer.populate()
