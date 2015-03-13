import sys
import os
import codecs
import json

sys.path.append('/home/leebird/Projects/django-annotation')
sys.path.append('/home/leebird/Projects/legonlp/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_nlp.settings")

import django
django.setup()

from django_annotation.models import *
from django_annotation.submodules.annotation.readers import AnnParser
from django.db import transaction

documents = list(Document.objects.only('doc_id').all())

relation_category = RelationCategory.objects.get(category='Phosphorylation')
gene_category = EntityCategory.objects.get(category='Gene')
# 
# relations = list(Relation.objects.select_related('doc').filter(category=relation_category))

exact_match = 0
end_count = 0
count = 0
for doc in documents:
    count += 1
    print('\r'+str(count), end='')
    exact_map = {}
    end_map = {}
    genes = list(doc.entity_set.filter(category=gene_category))
    for gene in genes:
        start = gene.start
        end = gene.end
        norm_ids = list(gene.entityproperty_set.filter(label='norm_id'))
        norm_ids = [nid.value for nid in norm_ids]
        exact_map[(start, end)] = norm_ids
        end_map[end] = norm_ids
        
    relations = list(doc.relation_set.filter(category=relation_category))
    for relation in relations:
        args = list(relation.entity_arguments.select_related('argument').all())
        for arg in args:
            entity = arg.argument
            if entity.category.category != 'Substrate' or entity.category.category != 'Kinase':
                continue
                
            start = entity.start
            end = entity.end
            
            if (start, end) in exact_map:
                exact_match += 1
            if end in end_map:
                end_count += 1
                
print(exact_match, end_count)