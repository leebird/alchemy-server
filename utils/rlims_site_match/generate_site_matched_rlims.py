import sys

from utils.alchemy_init import django_init

django_init()
from alchemy_server.models import *
from alchemy_restful.views.collection_api import CollectionAPI
from alchemy_restful.views.user_api import UserAPI

amino_acid_map = {'Ser': 'S', 'Thr': 'T', 'Tyr': 'Y'}

norm_collection = sys.argv[1]
entrez_uniprot_file = sys.argv[2]
fasta_file = sys.argv[3]
reviewed_uniprot_file = sys.argv[4]
kinase_uniprot_file = sys.argv[5]
result_file = sys.argv[6]

db_user = UserAPI.get_user(username='ligang', auth=False)
db_collection = CollectionAPI.get_collection(collection='RLIMS-P', user=db_user)
doc_ids = CollectionAPI.get_collection_docs(db_collection)
# doc_ids = ['10191262']
documents = Document.objects.only('id', 'doc_id').filter(id__in=doc_ids)

relation_category = RelationCategory.objects.get(category='Phosphorylation')
db_norm_collection = Collection.objects.get(collection=norm_collection)
gene_category = EntityCategory.objects.get(category='Gene', collection=db_norm_collection)
doc_count = 0

print('read entrez to uniprot AC mapping')
entrez2uniprot = {}
with open(entrez_uniprot_file, 'r') as handle:
    for line in handle:
        tokens = line.strip().split()
        if tokens[0] in entrez2uniprot:
            entrez2uniprot[tokens[0]].append(tokens[1])
        else:
            entrez2uniprot[tokens[0]] = [tokens[1]]
print('read', len(entrez2uniprot), 'mappings')

print('read fasta sequences')
uniprot2sequence = {}
with open(fasta_file, 'r') as handle:
    uniprot = None
    for line in handle:
        line = line.strip()
        if line.startswith('>'):
            tokens = line.split('|')
            uniprot = tokens[1]
            uniprot2sequence[uniprot] = ''
        else:
            uniprot2sequence[uniprot] += line
print('read', len(uniprot2sequence), 'sequences')

print('read reviewed uniprot ACs')
with open(reviewed_uniprot_file, 'r') as handle:
    text = handle.read().strip()
    reviewed_acs = set(text.split('\n'))
print('read', len(reviewed_acs), 'reviewed acs')

print('read kinase uniprot ACs')
with open(kinase_uniprot_file, 'r') as handle:
    text = handle.read().strip()
    kinase_acs = set(text.split('\n'))
print('read', len(kinase_acs), 'kinase acs')

print(len(documents), 'documents')

handle = open(result_file, 'w')
for doc in documents:
    doc_count += 1
    print('\r' + str(doc_count), end='')

    doc_id = doc.doc_id
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
    pmid_res_lines = set()
    for relation in relations:
        args = list(relation.entity_arguments.select_related('argument').all())
        # kinases, substrates, sites
        # [(kinase, (ids))], [(substrate, (ids))], [(amino_acid, site)]
        norm_rel = {'kinase': set(), 'substrate': set(), 'site': set()}

        for arg in args:
            entity = arg.argument
            start = entity.start
            end = entity.end

            norm_ids = []
            if (start, end) in exact_map:
                exact_match = True
                norm_ids = exact_map[(start, end)]

            if end in end_map:
                end_match = True

            uniprot_acs = set()
            for norm_id in norm_ids:
                if norm_id in entrez2uniprot:
                    uniprot_acs |= set(entrez2uniprot[norm_id])

            if arg.role.role == 'Substrate':
                norm_rel['substrate'].add((entity.text, tuple(uniprot_acs)))

            elif arg.role.role == 'Kinase':
                reviewed_kinase_acs = set()
                unreviewed_kinase_acs = set()
                for ac in uniprot_acs:
                    if ac in kinase_acs:
                        if ac in reviewed_acs:
                            reviewed_kinase_acs.add(ac)
                        else:
                            unreviewed_kinase_acs.add(ac)
                if len(reviewed_kinase_acs) > 0:
                    # reviewed and has keyword "Kinase" in uniprot annotation
                    # add all these ACs
                    norm_rel['kinase'].add((entity.text, tuple(reviewed_kinase_acs)))
                elif len(unreviewed_kinase_acs) > 0:
                    # not reviewed but has keyword "Kinase" in uniprot annotation
                    # add one of these ACs
                    norm_rel['kinase'].add((entity.text, tuple([unreviewed_kinase_acs.pop()])))
            elif arg.role.role == 'Site':
                try:
                    db_amino_acid = entity.entityproperty_set.filter(label='amino_acid')
                    db_position = entity.entityproperty_set.filter(label='position')
                except AttributeError:
                    continue
                if len(db_amino_acid) == 0 or len(db_position) == 0:
                    continue
                amino_acid = db_amino_acid[0].value
                position = int(db_position[0].value)
                norm_rel['site'].add((amino_acid, position))
            else:
                continue
                # print(count)

        # print(norm_rel)
        # no site
        if len(norm_rel['site']) == 0:
            continue
        # match substrate sequence with extracted site
        matched_substrate = set()
        for substrate, uniprot_acs in norm_rel['substrate']:
            matched_acs = set()
            for ac in uniprot_acs:
                sequence = uniprot2sequence.get(ac)
                if sequence is None:
                    continue
                matched = True
                for amino_acid, position in norm_rel['site']:
                    amino_acid_1 = amino_acid_map.get(amino_acid)
                    if amino_acid_1 is None:
                        matched = False
                        break
                    if position > len(sequence):
                        matched = False
                        break
                    if sequence[position - 1] != amino_acid_1:
                        matched = False
                        break

                if matched:
                    matched_acs.add(ac)
            if len(matched_acs) > 0:
                matched_substrate.add((substrate, tuple(matched_acs)))

        if len(matched_substrate) == 0:
            continue

        site_string = '|'.join([amino_acid + '-' + str(position) for amino_acid, position in norm_rel['site']])
        if len(norm_rel['kinase']) > 0:
            for substrate, substrate_acs in matched_substrate:
                for kinase, rlims_kinase_acs in norm_rel['kinase']:
                    res_line = '\t'.join([doc_id, kinase, substrate,
                                          '|'.join(rlims_kinase_acs),
                                          '|'.join(substrate_acs),
                                          site_string]) + '\n'
                    pmid_res_lines.add(res_line)
        else:
            for substrate, substrate_acs in matched_substrate:
                res_line = '\t'.join([doc_id, '', substrate,
                                      '',
                                      '|'.join(substrate_acs),
                                      site_string]) + '\n'
                pmid_res_lines.add(res_line)

    handle.write(''.join(pmid_res_lines))

handle.close()