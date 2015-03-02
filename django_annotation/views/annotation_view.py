from django.core.urlresolvers import reverse

from django_annotation.models import *
from django_annotation.utils.tagger import SpanTagger
from django_annotation.submodules.annotation.annotate import Entity
from django_annotation.forms import SearchPubMedForm

from .base_view import BaseView

class AnnotationView(BaseView):
    # annotation page
    template_name = BaseView.app_name + '/annotation.html'
    form_class = SearchPubMedForm
    view_name = 'annotation'

    styles = {'MiRNA':[('color','#c70d40'),('font-weight','bold')],
              'Gene':[('color','#0d40c7'),('font-weight','bold')],
              'Complex':[('color','blue'),('font-weight','bold')],
              'Family':[('color','blue'),('font-weight','bold')],
              'Trigger':[('text-decoration','underline'),('font-weight','bold')],
              }

    classes = {}

    tags = {'Sentence':'li'}

    argument_order = ['Agent','Theme']

    def get(self, request, doc_id):
        self.doc_id = doc_id
        return super(AnnotationView, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(AnnotationView, self).get_context_data(**kwargs)
        doc_id = self.doc_id
        doc = Document.objects.get(doc_id=doc_id)
        context['doc'] = doc

        doc_text = doc.text
        relations = list(doc.relation_set.all())
        sentences = list(doc.entity_set.filter(category__category='Sentence'))
        sentences.sort(key=lambda a:a.get_start())

        # map sentence id => sentence order
        sentid_sentpos = {}
        for sentpos,sent in enumerate(sentences):
            sentid_sentpos[sent.id] = sentpos+1

        args = []
        tuples = {}

        for rel in relations:
            rel_args = rel.relationargument_set.all()
            args += rel_args

            ordered_args = []
            for cat in self.argument_order:
                ordered_arg = [a for a in rel_args if a.get_arg_category() == cat]
                ordered_args.append(ordered_arg[0].get_text())

            row = tuple(ordered_args)
            if row not in tuples:
                tuples[row] = []

            for sent in sentences:
                for arg in rel_args:
                    if arg.get_start() >= sent.start and arg.get_end() <= sent.end:
                        tuples[row].append(sentid_sentpos[sent.id])

        for row,sents in tuples.items():
            tuples[row] = sorted(list(set(sents)))

        args = list(set(args))
        args += list(sentences)
        entities = []
        for arg in args:
            typing = arg.get_category()
            text = arg.get_text()
            start = arg.get_start()
            end = arg.get_end()
            entity = Entity(typing,start,end,text)
            entities.append(entity)

        tagged = SpanTagger.tag(doc_text,entities,self.tags,self.classes,self.styles)
        context['tagged'] = tagged
        context['tuples'] = tuples
        context['post_url'] = reverse('handle_search')
        return context