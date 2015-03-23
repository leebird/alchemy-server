import sys
import os
import pprint

sys.path.append('/home/leebird/Projects/alchemy-server')
sys.path.append('/home/leebird/Projects/legonlp/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alchemy_django.settings")

import django
django.setup()

from alchemy_server.models import *

norm_collection = sys.argv[1]

doc_id_file = None
if len(sys.argv) > 2:
    doc_id_file = sys.argv[2]

if doc_id_file is not None:
    with open(doc_id_file, 'r') as dh:
        text = dh.read().strip()
        doc_ids = text.split('\n')
        documents = list(Document.objects.only('doc_id').filter(doc_id__in=doc_ids))
else:
    documents = list(Document.objects.only('doc_id').all())

relation_category = RelationCategory.objects.get(category='Phosphorylation')
db_norm_collection = Collection.objects.get(collection=norm_collection)
gene_category = EntityCategory.objects.get(category='Gene',collection=db_norm_collection)

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

print('\n')
pprint.pprint(count)