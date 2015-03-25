import sys

from alchemy_init import django_init
django_init()
from alchemy_server.models import *

# get the normalization collection, e.g., Gennorm
norm_collection = sys.argv[1]

db_norm_collection = Collection.objects.get(collection=norm_collection)
gene_category = EntityCategory.objects.get(category='Gene',collection=db_norm_collection)

norm_ids = EntityProperty.objects.filter(entity__category=gene_category,label='norm_id')

entrez_ids = set()
for norm_id in norm_ids:
    entrez_ids.add(norm_id.value)
    # print(norm_id.value)
    
print('\n'.join(entrez_ids))