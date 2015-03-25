import sys
import os
import json

from alchemy_init import django_init
django_init()

from alchemy_restful.views.collection_api import CollectionAPI
from alchemy_restful.views.user_api import UserAPI
from alchemy_server.utils.transform import Document2Annotation
from alchemy_server.models.document import Document

username = sys.argv[1]
collection = sys.argv[2]
dump_path = sys.argv[3]

db_user = UserAPI.get_user(username=username, auth=False)
db_collection = CollectionAPI.get_collection(user=db_user, collection=collection)
docs = CollectionAPI.get_collection_docs(db_collection)

docs = list(docs)
print("%d documents" % len(docs))
step = 500
curr = 0

while True:
    doc_slice = docs[curr:curr+step]
    if len(doc_slice) == 0:
        break
    print(curr)
    curr += step
    documents = Document.objects.filter(id__in=doc_slice)
    transformer = Document2Annotation(documents, username, collection)
    annotations = transformer.transform()
    for annotation in annotations.values():
        json_path = os.path.join(dump_path, annotation.get('doc_id')+'.json')
        with open(json_path, 'w') as jh:
            jh.write(json.dumps(annotation)+'\n')
