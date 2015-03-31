import sys

alchemy_file = sys.argv[1]
alanine_file = sys.argv[2]
add_to_file = sys.argv[3]

# pmid -> [(kinase_ids, substrate_ids, sites)]
alchemy_id_hash = {}
# pmid -> [(kinase, substrate, sites)]
alchemy_name_hash = {}

with open(alchemy_file, 'r') as handle:
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        pmid = tokens[0]
        kinase = tokens[1].lower()
        substrate = tokens[2].lower()
        kinase_ids = set(tokens[3].split('|'))
        substrate_ids = set(tokens[4].split('|'))
        sites = set(tokens[5].split('|'))
        try:
            alchemy_name_hash[pmid].append((kinase, substrate, sites))
        except KeyError:
            alchemy_name_hash[pmid] = [(kinase, substrate, sites)]
        try:
            alchemy_id_hash[pmid].append((kinase_ids, substrate_ids, sites))
        except KeyError:
            alchemy_id_hash[pmid] = [(kinase_ids, substrate_ids, sites)]

add_count = 0
with open(alanine_file, 'r') as handle, open(add_to_file, 'w') as add_handle:
    for line in handle:
        line = line.strip()
        tokens = line.split('\t')
        pmid = tokens[0]
        kinase = tokens[1].lower()
        substrate = tokens[2].lower()
        kinase_ids = set(tokens[3].split('|'))
        substrate_ids = set(tokens[4].split('|'))
        sites = set(tokens[5].split('|'))
        
        # flag for whether the alanine result is new to alchemy result
        add_flag = True

        # check by kinase/substrate name
        try:
            triples = alchemy_name_hash[pmid]
            for triple in triples:
                if (len(kinase) == 0 or triple[0] == kinase) and \
                   (len(substrate) == 0 or triple[1] == substrate) and \
                   triple[2].issuperset(sites):
                    add_flag = False
                    break
        except KeyError:
            add_handle.write(line + '\n')
            add_count += 1
            continue

        if not add_flag: 
            continue

        # check by kinsae/substrate ids
        try:
            triples = alchemy_id_hash[pmid]
            for triple in triples:
                if (triple[0].issuperset(kinase_ids) or kinase_ids.issuperset(triple[0])) and \
                   triple[1].issuperset(substrate_ids) or substrate_ids.issuperset(triple[1]) and \
                   triple[2].issuperset(sites):
                    add_flag = False
                    break
        except KeyError:
            add_handle.write(line + '\n')
            add_count += 1
            continue

        if add_flag:
            add_handle.write(line + '\n')
            add_count += 1
        
            
print(add_count)
