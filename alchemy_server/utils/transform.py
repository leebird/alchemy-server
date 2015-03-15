from alchemy_server.models import *
import json


class Document2BioNLP(object):
    """
    output a set of documents and their entities and relations
    to brat embedding format. About brat embedding format: 
    http://brat.nlplab.org/embed.html
    """

    def __init__(self, documents):
        self.documents = documents

    def transform(self):
        res = {}
        for doc in self.documents:
            doc_id = doc.doc_id
            res[doc_id] = self.transform_document(doc)
        return res

    def transform_document(self, document):
        doc = {}
        entities, triggers, id2tid = self.transform_entity(document.entity_set.all())
        triggers, events = self.transform_event(document.relation_set.all(), triggers, id2tid)
        doc['text'] = document.text
        doc['entities'] = entities
        doc['triggers'] = list(triggers.values())
        doc['events'] = events
        return doc

    @staticmethod
    def transform_entity(entity_list):
        """ get document's entities in bionlp format. 
        positions are actually a list of tuples, which are all lists in javascript.
        [tid,type,[[start,end]]]
        ['T1','Protein',[[10,20]]]
        """
        entities = []
        triggers = {}
        id2tid = {}
        for i, t in enumerate(entity_list):
            typing = t.category.category
            tid = 'T' + str(i + 1)
            try:
                start = t.start
                end = t.end
                if typing == 'Trigger':
                    triggers[tid] = [tid, typing, ((start, end),)]
                else:
                    entities.append((tid, typing, ((start, end),)))
                id2tid[t.id] = tid
            except KeyError:
                pass
        return entities, triggers, id2tid

    @staticmethod
    def transform_event(relation_list, triggers, id2tid):
        """ get document's relations in bionlp format
        """
        relations = []
        for i, relation in enumerate(relation_list):
            args = relation.entity_arguments.all()
            is_event = False
            arg_tuples = []
            trigger_id = None
            for arg in args:
                tid = id2tid.get(arg.argument.id)
                arg_role = arg.role.role
                if arg_role == 'Trigger':
                    is_event = True
                    trigger_id = tid
                    trigger = triggers[tid]
                    trigger[1] = relation.category.category
                    continue
                arg_tuples.append((arg_role, tid))
            
            if not is_event:
                continue
            
            rid = 'E' + str(i + 1)
            relations.append((rid, trigger_id, arg_tuples))
        return triggers, relations

    @staticmethod
    def transform_relation(relation_list, triggers, id2tid):
        """ get document's relations in bionlp format
        """
        relations = []
        for i, relation in enumerate(relation_list):
            args = relation.entity_arguments.all()
            prefix = 'R'
            arg_tuples = []
            trigger_id = None
            for arg in args:
                tid = id2tid.get(arg.argument.id)
                arg_role = arg.role.role
                if arg_role == 'Trigger':
                    prefix = 'E'
                    trigger_id = tid
                    trigger = triggers[tid]
                    trigger[1] = relation.category.category
                    continue
                arg_tuples.append((arg_role, tid))

            if prefix == 'R':
                continue

            rid = prefix + str(i + 1)
            typing = relation.category.category
            relations.append((rid, trigger_id, typing, arg_tuples))
        return triggers, relations

    @staticmethod
    def transform_attribute(attributes):
        """ get attribute hash for an entitiy
        key is attribute name, value is a list of corresponding values
        mandatory attribute: type
        """
        res = {}
        for a in attributes:
            prop = a.attribute
            val = a.value
            if prop in res:
                res[prop].append(val)
            else:
                res[prop] = [val]
        return res

class Document2Annotation(object):
    """
    output a set of documents and their entities and relations
    to annotation format.
    """

    def __init__(self, documents):
        self.documents = documents

    def transform(self):
        res = {}
        for doc in self.documents:
            doc_id = doc.doc_id
            res[doc_id] = self.transform_document(doc)
        return res

    def transform_document(self, document):
        doc = {}
        entities, id2tid = self.transform_entity(document.entity_set.all())
        relations = self.transform_relation(document.relation_set.all(), id2tid)
        doc['text'] = document.text
        doc['entities'] = entities
        doc['relations'] = relations
        return doc

    def transform_entity(self, entity_list):
        """
        get document's entities in bionlp format.
        positions are actually a list of tuples, which are all lists in javascript.
        [tid,type,[[start,end]]]
        ['T1','Protein',[[10,20]]]
        """
        entities = []
        id2tid = {}
        temp_id = 1
        
        for entity in entity_list:
            try:
                tid = entity.entity_property_set.get(label='id')
            except:
                tid = 'TT' + str(temp_id)
                temp_id += 1
            try:
                typing = entity.category.category
                start = entity.start
                end = entity.end
                entities.append((tid, typing, ((start, end),)))
                id2tid[entity.id] = tid
            except KeyError:
                pass
        return entities, id2tid

    def transform_relation(self, relation_list, id2tid):
        """
        get document's relations in bionlp format
        """
        relations = []
        temp_id = 1
        for relation in relation_list:
            try:
                rid = relation.relation_property_set.get(label='id')
            except:
                rid = 'RR' + str(temp_id)
                temp_id += 1
                
            args = relation.relationargument_set.all()
            typing = relation.category.category
            
            arg_tuples = []
            for arg in args:
                tid = id2tid[arg.argument.id]
                arg_role = arg.category.category
                arg_tuples.append((arg_role, tid))
            relations.append((rid, typing, arg_tuples))
            
        return relations


    def transform_attribute(self, attributes):
        """
        get attribute hash for an entity
        key is attribute name, value is a list of corresponding values
        mandatory attribute: type
        """
        res = {}
        for a in attributes:
            prop = a.attribute
            val = a.value
            if prop in res:
                res[prop].append(val)
            else:
                res[prop] = [val]
        return res

class Document2Relation:
    """
    output a specific relation of a set of documents into tuples
    """

    def __init__(self, documents, relationType):
        self.documents = documents
        self.relationType = relationType
        self.positiveDocNum = 0

    def transform(self):
        res = {}
        for doc in self.documents:
            doc_id = doc.doc_id.encode('utf-8')
            res[doc_id] = self.transform_document(doc)
        return res

    def transform_document(self, document):
        # doc = {}
        #entities,id2tid = self.transform_entity(document.entity_set.all())
        relationSet = document.relation_set.filter(category=self.relationType)
        relations = self.transform_relation(relationSet)
        #doc['text'] = document.text.encode('utf-8')
        #doc['entities'] = entities
        #doc['relations'] = relations
        if len(relations) > 0:
            self.positiveDocNum += 1
        return relations

    def transform_relation(self, relationList):
        """
        get document's relations into tuples
        """
        relations = []
        for i, r in enumerate(relationList):
            args = r.relationargument_set.all()
            argTuples = []
            for arg in args:
                argType = arg.category.category
                argText = arg.argument.text
                argTuples.append((argType, argText))
            relations.append(argTuples)
        return relations

    def transform_attribute(self, attributes):
        """
        get attribute hash for an entitiy
        key is attribute name, value is a list of corresponding values
        mandatory attribute: type
        """
        res = {}
        for a in attributes:
            prop = a.attribute
            val = a.value
            if res.has_key(prop):
                res[prop].append(val)
            else:
                res[prop] = [val]
        return res

