class Document2BioNLP(object):
    '''
    output a set of documents and their entities and relations
    to brat embedding format. About brat embedding format: 
    http://brat.nlplab.org/embed.html
    '''
    def __init__(self,documents):
        self.documents = documents

    def transform(self):
        res = {}
        for doc in self.documents:
            doc_id = doc.doc_id.encode('utf-8')
            res[doc_id] = self.transform_document(doc)
        return res

    def transform_document(self,document):
        doc = {}
        entities,id2tid = self.transform_entity(document.entity_set.all())
        relations = self.transform_relation(document.relation_set.all(),id2tid)
        doc['text'] = document.text.encode('utf-8')
        doc['entities'] = entities
        doc['relations'] = relations
        return doc

    def transform_entity(self,entityList):
        '''
        get document's entities in bionlp format. 
        positions are actually a list of tuples, which are all lists in javascript.
        [tid,type,[[start,end]]]
        ['T1','Protein',[[10,20]]]
        '''
        entities = []
        id2tid = {}
        for i,t in enumerate(entityList):            
            tid = 'T'+str(i+1)
            try:
                typing = t.category.category
                start = t.start
                end = t.end
                entities.append((tid,typing,((start,end),)))
                id2tid[t.id] = tid
            except KeyError:
                pass
        return entities,id2tid

    def transform_relation(self,relationList,id2tid):
        '''
        get document's relations in bionlp format
        '''
        relations = []
        for i,r in enumerate(relationList):
            rid = 'R' + str(i+1)
            args = r.relationargument_set.all()
            typing = r.category.category
            argTuples = []
            for arg in args:
                tid = id2tid[arg.argument.id]
                argType = arg.category.category
                argTuples.append((argType,tid))
            relations.append((rid,typing,argTuples))
        return relations
    
    def transform_attribute(self,attributes):
        '''
        get attribute hash for an entitiy
        key is attribute name, value is a list of corresponding values
        mandatory attribute: type
        '''
        res = {}
        for a in attributes:
            prop = a.attribute
            val = a.value
            if res.has_key(prop):
                res[prop].append(val)
            else:
                res[prop] = [val]
        return res

class Document2Relation:
    '''
    output a specific relation of a set of documents into tuples
    '''
    def __init__(self,documents,relationType):
        self.documents = documents
        self.relationType = relationType
        self.positiveDocNum = 0

    def transform(self):
        res = {}
        for doc in self.documents:
            doc_id = doc.doc_id.encode('utf-8')
            res[doc_id] = self.transform_document(doc)
        return res

    def transform_document(self,document):
        #doc = {}
        #entities,id2tid = self.transform_entity(document.entity_set.all())
        relationSet = document.relation_set.filter(category=self.relationType)
        relations = self.transform_relation(relationSet)
        #doc['text'] = document.text.encode('utf-8')
        #doc['entities'] = entities
        #doc['relations'] = relations
        if len(relations) > 0:
            self.positiveDocNum += 1
        return relations

    def transform_relation(self,relationList):
        '''
        get document's relations into tuples
        '''
        relations = []
        for i,r in enumerate(relationList):
            args = r.relationargument_set.all()
            argTuples = []
            for arg in args:
                argType = arg.category.category
                argText = arg.argument.text
                argTuples.append((argType,argText))
            relations.append(argTuples)
        return relations
    
    def transform_attribute(self,attributes):
        '''
        get attribute hash for an entitiy
        key is attribute name, value is a list of corresponding values
        mandatory attribute: type
        '''
        res = {}
        for a in attributes:
            prop = a.attribute
            val = a.value
            if res.has_key(prop):
                res[prop].append(val)
            else:
                res[prop] = [val]
        return res

