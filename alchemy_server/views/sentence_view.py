from django.core.urlresolvers import reverse

from alchemy_server.models import *
from alchemy_server.utils.tagger import SpanTagger
from submodules.annotation.annotate import Entity

from .annotation_view import AnnotationView

class SentenceView(AnnotationView):

    view_name = 'sentence'

    def get(self, request, doc_id, rel_id):
        self.doc_id = doc_id
        self.rel_id = rel_id.strip().split(',')
        return super(SentenceView, self).get(request, doc_id)

    def get_context_data(self, **kwargs):
        context = super(SentenceView, self).get_context_data(**kwargs)
        doc = Document.objects.get(doc_id=self.doc_id)
        context['doc'] = doc

        doc_text = doc.text
        relations = list(doc.relation_set.filter(id__in=self.rel_id))
        sentences = list(doc.entity_set.filter(category__category='Sentence'))

        # map sentence id => sentence order
        sentid_sentpos = {}
        for sentpos,sent in enumerate(sentences):
            sentid_sentpos[sent.id] = sentpos+1

        args = []
        tuples = {}

        for rel in relations:
            rel_args = list(rel.relationargument_set.all())
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

        # make highligted text
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