import re
import sys
import os

uniprot_text_file = sys.argv[1]

root_folder = os.path.dirname(os.path.abspath(__file__))

f = open(uniprot_text_file, 'r')

unreviewed = {}
reviewed = {}
kinasekey = {}
kinasename = {}

is_reviewed = False
is_unreviewed = False
pattern = r'^Name[:=](.*?);'

for line in f:
    line = line.rstrip()
    if line.startswith('AC'):
        ac = line[5:].split(';')[0].strip()
        if is_unreviewed:
            unreviewed[ac] = 1
        if is_reviewed:
            reviewed[ac] = 1

    if line.startswith('ID'):
        if line.find('Unreviewed') != -1:
            is_unreviewed = True
        elif line.find('Reviewed') != -1:
            is_reviewed = True

    if line.startswith('GN'):
        gene = line[5:].strip()
        match = re.search(pattern, gene)
        if match:
            name = match.group(1).lower()
            kinasename[ac] = name
        else:
            kinasename[ac] = gene

    if line.startswith('KW'):
        if line.find('; Kinase;') != -1 or line.find('   Kinase;') != -1:
            kinasekey[ac] = 1

    if line.startswith('//'):
        if ac not in kinasename:
            kinasename[ac] = ac
        is_unreviewed = False
        is_reviewed = False
f.close()

f = open(os.path.join(root_folder, 'data/unreviewed'), 'w')
for key, val in unreviewed.items():
    f.write(key + '\n')
f.close()

f = open(os.path.join(root_folder, 'data/reviewed'), 'w')
for key in reviewed.keys():
    f.write(key + '\n')
f.close()

f = open(os.path.join(root_folder, 'data/kinasekey'), 'w')
for key in kinasekey.keys():
    f.write(key + '\n')
f.close()

f = open(os.path.join(root_folder, 'data/kinasename'), 'w')
for key, val in kinasename.items():
    f.write(key + '\t' + val + '\n')
f.close()
