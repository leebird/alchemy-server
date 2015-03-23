from alchemy_server.models import *
import json


class Document2BioNLP(object):
    """ output a set of documents and their entities and relations
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
        db_relations = document.relation_set.all()
        triggers, events, relations = self.transform_relation(db_relations, triggers, id2tid)
        doc['text'] = document.text
        doc['entities'] = entities
        doc['triggers'] = list(triggers.values())
        doc['events'] = events
        doc['relations'] = relations
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
    def transform_relation(relation_list, triggers, id2tid):
        """ get document's relations in bionlp format
        """
        events = []
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

            if is_event:
                rid = 'E' + str(i + 1)
                events.append((rid, trigger_id, arg_tuples))
            else:
                rid = 'R' + str(i + 1)
                relations.append((rid, relation.category.category, arg_tuples))
        return triggers, events, relations

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
    """ output a set of documents and their entities and relations
    to annotation format.
    """

    def __init__(self, documents, username=None, collection=None):
        self.documents = documents
        if username is not None and collection is not None:
            self.user = User.objects.get(username=username)
            self.collection = Collection.objects.get(user=self.user, collection=collection)
            self.entity_category = EntityCategory.objects.filter(collection=self.collection)
            self.relation_category = RelationCategory.objects.filter(collection=self.collection)
        else:
            self.user = None
            self.collection = None

    def transform(self):
        res = {}
        for doc in self.documents:
            doc_id = doc.doc_id
            res[doc_id] = self.transform_document(doc)
        return res

    def transform_document(self, document):
        doc = {}
        if self.collection is None:
            entity_set = document.entity_set.all()
            relation_set = document.relation_set.all()
        else:
            entity_set = document.entity_set.filter(category__in=self.entity_category)
            relation_set = document.relation_set.filter(category__in=self.relation_category)

        entities = self.transform_entity(entity_set)
        relations = self.transform_relation(relation_set)
        properties = self.transform_property(document.documentproperty_set.all())
        doc['text'] = document.text
        doc['entity_set'] = entities
        doc['relation_set'] = relations
        doc['property'] = properties
        doc['doc_id'] = document.doc_id
        return doc

    def transform_entity(self, entity_list):
        """ get document's entities in annotation format.
        """
        entities = []

        for entity in entity_list:
            tid = entity.uid
            category = entity.category.category
            start = entity.start
            end = entity.end
            text = entity.text
            properties = entity.entityproperty_set.all()
            ent_property = self.transform_property(properties)

            entities.append({
                'id': tid,
                'category': category,
                'start': start,
                'end': end,
                'text': text,
                'property': ent_property
            })
        return entities

    def transform_relation(self, relation_list):
        """ get document's relations in annotation format
        """
        relations = []
        for relation in relation_list:
            rid = relation.uid
            entity_args = relation.entity_arguments.all()
            relation_args = relation.relation_arguments.all()
            category = relation.category.category

            arg_tuples = []
            for arg in entity_args:
                tid = arg.argument.uid
                arg_role = arg.role.role
                arg_tuples.append((arg_role, tid))

            for arg in relation_args:
                tid = arg.argument.property.get('id')
                arg_role = arg.role.role
                arg_tuples.append((arg_role, tid))

            properties = relation.relationproperty_set.all()
            rel_property = self.transform_property(properties)

            relations.append({
                'id': rid,
                'category': category,
                'argument_set': arg_tuples,
                'property': rel_property
            })

        return relations

    def transform_property(self, db_properties):
        """ get property from QuerySet property_set
        """
        property = {}
        for db_property in db_properties:
            label = db_property.label
            value = db_property.value
            if label in property:
                if isinstance(property[label], list):
                    property[label].append(value)
                else:
                    property[label] = [property[label], value]
            else:
                property[label] = value
        return property
