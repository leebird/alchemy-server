import sys
import os
import codecs

sys.path.append('/var/www/django/v3')
sys.path.append('/home/leebird/bitbucket/annotation')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v3.settings")

from django_tm.models import *
from readers import AnnReader
from django.db import transaction

class Importer:
    '''
    populate database with data in a folder
    '''

    def __init__(self,path):
        self.path = path
        self.entityType = {}
        self.relationType = {}
        self.argumentType = {}
        self.filename = None

    @transaction.atomic
    def populate(self):
        reader = AnnReader()
        for root,_,files in os.walk(self.path):
            for f in files:
                if not f.endswith('.txt'):
                    continue

                txt = codecs.open(os.path.join(root,f),'r','utf-8')
                text = txt.read()
                txt.close()

                self.filename = f[:-4]
                ann = os.path.join(root, self.filename+'.ann')
                anno = reader.parse_file(ann)
                
                self.process_document(text,anno)
        
    def process_document(self, text, annotation):
        d = Document(doc_id=self.filename,text=text)
        d.save()

        tid2entity = {}

        if annotation is None:
            return

        self.add_entity(d, annotation.get_entities().values(), tid2entity)
        self.add_relation(d, annotation.get_relations().values(), tid2entity)
        self.add_event(d, annotation.get_events().values(), tid2entity)

    def add_entity(self, doc, entityList, tid2entity):
        for t in entityList:
            typing = self.get_entity_type(t.type)
            entity = Entity(doc=doc, category=typing, start=t.start, end=t.end, text=t.text)
            entity.save()
            tid2entity[t.id] = entity

    def add_relation(self, doc, relationList, tid2entity):
        for r in relationList:
            typing = self.get_relation_type(r.type)
            relation = Relation(doc=doc, category=typing)
            relation.save()

            arg0 = tid2entity[r.arg1[1].id]
            arg1 = tid2entity[r.arg2[1].id]

            arg0Type = self.get_argument_type(relation.category,arg0.category,'Agent')
            arg1Type = self.get_argument_type(relation.category,arg1.category,'Theme')

            relationArg = RelationArgument(category=arg0Type,
                                           relation=relation,
                                           argument=arg0)

            relationArg.save()
            relationArg = RelationArgument(category=arg1Type,
                                           relation=relation,
                                           argument=arg1)

            relationArg.save()


    def add_event(self, doc, eventList, tid2entity):
        for e in eventList:
            typing = self.get_relation_type(e.type)
            relation = Relation(doc=doc, category=typing)
            relation.save()

            arg0 = tid2entity[e.args[0][1].id]
            arg1 = tid2entity[e.args[1][1].id]

            arg0Type = self.get_argument_type(relation.category,arg0.category,'Agent')
            arg1Type = self.get_argument_type(relation.category,arg1.category,'Theme')

            relationArg = RelationArgument(category=arg0Type,
                                           relation=relation,
                                           argument=arg0)

            relationArg.save()
            relationArg = RelationArgument(category=arg1Type,
                                           relation=relation,
                                           argument=arg1)

            relationArg.save()

            trigger = tid2entity[e.trigger.id]
            triggerType = self.get_argument_type(relation.category,trigger.category,'Trigger')
            relationArg = RelationArgument(category=triggerType,
                                           relation=relation,
                                           argument=trigger)
            relationArg.save()

            for key, values in e.prop.prop.iteritems():
                values = set(values)
                for value in values:
                    relation.relationattribute_set.create(attribute=key,value=value)

    def get_entity_type(self,category):
        '''
        get entity type from database or local cache
        '''
        if self.entityType.has_key(category):
            return self.entityType[category]
        typing = EntityType.objects.filter(category=category)

        if len(typing) == 0:
            raise KeyError('Entity type is not defined',category)

        self.entityType[category] = typing[0]
        return typing[0]

    def get_relation_type(self,category):
        '''
        get relation type from database or local cache
        '''
        if self.relationType.has_key(category):
            return self.relationType[category]
        typing = RelationType.objects.filter(category=category)

        if len(typing) == 0:
            raise KeyError('Relation type is not defined')

        self.relationType[category] = typing[0]
        return typing[0]

    def get_argument_type(self, relationType, entityType, category):
        '''
        get argument type from database or local cache
        relation, entity and category define an argument type
        relation and category can be linked to multiple types of entities
        e.g., Target's theme could be protein or complex
        '''
        #print relationType,entityType,category
        if self.argumentType.has_key((relationType.category,entityType.category,category)):
            return self.argumentType[(relationType.category,entityType.category,category)]
        typing = ArgumentType.objects.filter(relation_type=relationType,
                                             entity_type=entityType,
                                             category=category)

        if len(typing) == 0:
            raise KeyError('Argument type is not defined')

        self.argumentType[(relationType.category,entityType.category,category)] = typing[0]
        return typing[0]

importer = Importer('/var/www/django/v3/django_tm/data')
importer.populate()
