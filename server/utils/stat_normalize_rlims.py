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

count = {
    'total': 0,
    'exact_match': 0,
    'end_match': 0,
    'kinase_total': 0,
    'substrate_total': 0,
    'kinase_exact': 0,
    'kinase_end': 0,
    'substrate_exact': 0,
    'substrate_end': 0
}

doc_count = 0

for doc in documents:
    doc_count += 1
    print('\r' + str(doc_count), end='')
    
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
            exact_match = 0
            end_match = 0
            entity = arg.argument
            start = entity.start
            end = entity.end

            if (start, end) in exact_map:
                exact_match = 1
            if end in end_map:
                end_match = 1
            
            if arg.role.role == 'Substrate':
                count['total'] += 1
                count['substrate_total'] += 1
                count['exact_match'] += exact_match
                count['end_match'] += end_match
                count['substrate_exact'] += exact_match
                count['substrate_end'] += end_match
                
            elif arg.role.role == 'Kinase':
                count['total'] += 1
                count['kinase_total'] += 1
                count['exact_match'] += exact_match
                count['end_match'] += end_match
                count['kinase_exact'] += exact_match
                count['kinase_end'] += end_match
            else:
                continue
    # print(count)


print('\n', count)