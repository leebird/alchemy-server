import sys
import pprint

from alchemy_init import django_init
django_init()
from alchemy_server.models import *

norm_collection = sys.argv[1]

relation_category = RelationCategory.objects.get(category='Phosphorylation')
db_norm_collection = Collection.objects.get(collection=norm_collection)
gene_category = EntityCategory.objects.get(category='Gene',collection=db_norm_collection)