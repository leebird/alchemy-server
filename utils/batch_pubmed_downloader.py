import sys
import os

from alchemy_init import django_init
django_init()

from .document_retriever import DocumentRetriever
import time

pmid_list = sys.argv[1]
step = 500
curr = 0

with open(pmid_list, 'r') as handle:
    pmid_text = handle.read().replace('\r', '\n').strip()
    pmids = pmid_text.split('\n')
    while True:
        pmid_slice = set(pmids[curr:curr + step])
        if len(pmid_slice) == 0:
            break
        
        print(curr)
        DocumentRetriever.retrieve(pmid_slice, is_retrieve=False)
        curr += step
        time.sleep(3)