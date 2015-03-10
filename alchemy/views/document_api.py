from django.views.generic import View
from django_annotation.models import *
from django.http import JsonResponse
from alchemy.utils.document_retriever import DocumentRetriever
import json
import traceback, sys


class DocumentAPI(View):
    view_name = 'document_api'

    def post(self, request):
        documents = request.POST.get('document_set')
        try:
            pmid_list = set(json.loads(documents))
            doc_text = DocumentRetriever.retrieve(pmid_list)
            return JsonResponse(doc_text)
        except:
            traceback.print_exc(file=sys.stderr)
            return JsonResponse({'success': False})

    def get(self, request, pmid):
        medlines = DocumentRetriever.retrieve({pmid})
        return JsonResponse(medlines, safe=False)

    @classmethod
    def get_document(cls, doc_id):
        try:
            document = Document.objects.get(doc_id=doc_id)
            return document
        except (Document.DoesNotExist, Document.MultipleObjectsReturned):
            return None

    @classmethod
    def save_document(cls, doc_id, text):
        document = cls.get_document(doc_id)
        if document:
            return document
        else:
            doc = Document(doc_id=doc_id, text=text)
            doc.save()
            return doc