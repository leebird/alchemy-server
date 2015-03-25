import sys

from alchemy_init import django_init
django_init()

from alchemy_server.models import *

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Specify collection to delete')
        sys.exit(0)

    collection = sys.argv[1]
    db_collection = Collection.objects.get(collection=collection)
    print(db_collection)

    entity_categories = EntityCategory.objects.filter(collection=db_collection)
    relation_categories = RelationCategory.objects.filter(collection=db_collection)

    # delete relation first
    for rc in relation_categories:
        print("deleting relation category " + rc.category)
        rc.delete()

    for ec in entity_categories:
        print("deleting entity category " + ec.category)
        ec.delete()

    print("deleting collection " + str(db_collection))
    db_collection.delete()
