from django.views.generic import TemplateView, FormView
from alchemy_server.models import *
from alchemy_server.utils.transform import Document2BioNLP
import json
from alchemy_server.forms import SearchPubMedForm
from .base_view import BaseView

class BratView(FormView):
    # annotation page
    view_name = 'brat'
    template_name = 'alchemy_server/brat.html'
    form_class = SearchPubMedForm
    app_name = 'alchemy_server'
    
    def get(self, request, doc_ids):

        self.doc_ids = doc_ids
        doc_id_list = doc_ids.strip().split(',')

        docs = Document.objects.filter(doc_id__in=doc_id_list)
        transformer = Document2BioNLP(docs)
        self.annotations = transformer.transform()
        # self.entity_categories = set([t[1] for doc in self.annotations.values() for t in doc.get('entities')])

        return super(BratView, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(BratView, self).get_context_data(**kwargs)
        context['doc_list'] = json.dumps(self.annotations)
        context['app_name'] = self.app_name
        # context['entity_categories'] = self.entity_categories
        # print(self.entity_categories)
        return context