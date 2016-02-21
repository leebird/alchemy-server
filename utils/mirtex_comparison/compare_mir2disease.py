import re
import sys
from utils.alchemy_init import django_init

django_init()
from alchemy_server.models import *
from alchemy_restful.views.collection_api import CollectionAPI
from alchemy_restful.views.user_api import UserAPI

mir2disease_file = sys.argv[1]
mir2disease_hash = {}

pattern = re.compile(r'[0-9]+')
mirtex_pattern = re.compile(r'(let|lin|micorR|miR|miRNA|microRNA|micro RNA)s?[\- x_]?([0-9]+)', re.IGNORECASE)

with open(mir2disease_file, 'r') as handle:
    for line in handle:
        line = line.strip()
        if ',' not in line:
            continue
        fields = line.split(',')
        pmid = fields[2].strip()
        mirna = fields[1].strip()
        gene = fields[3].strip().lower()

        match = pattern.search(mirna)
        if match is None:
            print('miRNA number not found:', mirna, file=sys.stderr)
            continue

        number = match.group()

        try:
            mir2disease_hash[pmid].add((pmid, number, gene))
        except KeyError:
            mir2disease_hash[pmid] = {(pmid, number, gene)}

print('read', len(mir2disease_hash), 'pmids')

db_user = UserAPI.get_user(username='ligang', auth=False)
db_collection = CollectionAPI.get_collection(collection='miRTex', user=db_user)
relation_category = RelationCategory.objects.get(category='miRNA2Gene')

all_set = set()
tp_set = set()
fn_set = set()

for pmid, pairs in mir2disease_hash.items():
    all_set |= pairs
    relations = Relation.objects.filter(doc__doc_id=pmid, category=relation_category)
    db_pairs = set()
    for relation in relations:
        arguments = relation.entity_arguments.all()
        gene = None
        mirna = None
        for arg in arguments:
            entity = arg.argument
            if arg.role.role == 'Theme':
                gene = entity.text.lower()
                if gene.endswith(('mrna','gene','protein')):
                    last = gene.rfind(' ')
                    if last != -1:
                        gene = gene[:last]
            elif arg.role.role == 'Agent':
                mirna = entity.text
            else:
                continue
        if gene is None or mirna is None:
            print('missing argument:', pmid, arguments, file=sys.stderr)
            continue

        match = mirtex_pattern.search(mirna)
        if match is None:
            print('db miRNA number not found:', pmid, mirna, file=sys.stderr)
            continue

        number = match.group(2)
        db_pairs.add((pmid, number, gene))

    tp_set |= pairs & db_pairs
    fn_set |= pairs - db_pairs

all = len(all_set)
tp = len(tp_set)
fn = len(fn_set)
recall = tp / all
print(all)
print(recall)
print('\n'.join(['\t'.join(fn) for fn in fn_set]))
