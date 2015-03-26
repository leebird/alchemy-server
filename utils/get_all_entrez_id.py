import sys

from alchemy_init import django_init
django_init()
from alchemy_server.models import *

import re
pattern = re.compile(r'[0-9]+')

# get the normalization collection, e.g., Gennorm
norm_collection = sys.argv[1]

db_norm_collection = Collection.objects.get(collection=norm_collection)
gene_category = EntityCategory.objects.get(category='Gene',collection=db_norm_collection)

norm_ids = EntityProperty.objects.filter(entity__category=gene_category,label='norm_id')

entrez_ids = set()
for norm_id in norm_ids:
    match = pattern.search(norm_id.value)
    if match is None:
        continue
    entrez_ids.add(match.group())
    # print(norm_id.value)
    
print('\n'.join(entrez_ids))
