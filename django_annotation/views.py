import json
import csv
import logging

from collections import OrderedDict
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.views import generic
from django.template import RequestContext
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, FormMixin
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django_annotation.models import *
from django_annotation.utils.transform import *
from django_annotation.utils.query_processor import QueryProcessor
from django_annotation.utils.tagger import SpanTagger
from annotation.annotation import Entity
from django_annotation.forms import SearchPubMedForm

class BaseView(FormView):
    # make app name visible for all child classes
    app_name = 'django_annotation'

    def get_context_data(self,**kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        context['app_name'] = self.app_name
        context['top_form'] = True
        return context

class IndexView(BaseView):
    # index page
    template_name = BaseView.app_name + '/index.html'
    form_class = SearchPubMedForm

    def form_valid(self, form):
        query = form.cleaned_data['query']
        return redirect(SearchView.view_name,query)

    def form_invalid(self, form):
        return redirect("index")

    def get(self, request):
        self.request = request
        return super(IndexView, self).get(request)

    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['top_form'] = False
        context['request'] = self.request
        context['post_url'] = reverse('handle_search')
        return context

class ContactView(BaseView):
    # contact page
    template_name = BaseView.app_name + '/contact.html'
    form_class = SearchPubMedForm

    def get(self, request):
        self.request = request
        return super(ContactView, self).get(request)

    def get_context_data(self,**kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['top_form'] = True
        context['request'] = self.request
        return context

class SearchView(BaseView):
    # search page
    template_name = BaseView.app_name + '/search.html'
    form_class = SearchPubMedForm

    view_name = 'search'
    processor = QueryProcessor()
    page_size = 10
    argument_order = ['Agent','Theme']
    download = False

    def make_pages(self, page, pmids):
        paginator = Paginator(pmids,self.page_size)

        try:
            current_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            current_page = paginator.page(1)
            page = 1
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            current_page = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        # get page numbers before and after the current page
        prev = page - 2 if page - 2 > 1 else 2
        post = page + 3 if page + 3 < paginator.num_pages else paginator.num_pages

        pages = {'first':1}
        pages['prev'] = range(prev,page) if prev < page else []
        pages['curr'] = page
        pages['post'] = range(page+1,post) if post > page else []
        pages['last'] = paginator.num_pages
        pages['next'] = page + 1 if page+1 < pages['last'] else pages['last']
        pages['before'] = page - 1 if page - 1 > 0 else 1
        return current_page.object_list, pages

    def get(self, request, query):
        pmids = self.processor.get_pmids(query)

        page = request.GET.get('page')
        page = 1 if page is None else int(page)

        self.original_query = query
        self.query = query
        self.genes = self.processor.get_lines(query)
        self.genes.reverse()
        self.stat = {}

        self.stat["pubmed_length"] = len(pmids)

        # all pmids
        docs = list(Document.objects.filter(doc_id__in=pmids))

        # pagintion
        '''
        docs = list(Document.objects.filter(doc_id__in=pmids))
        slide, pages = self.make_pages(page,docs)
        '''

        self.stat["positive_doc_length"] = len(docs)

        # get current page's docs
        # docs = slide

        tuples = {}
        rel_sentids = {}
        sentid_sent = {}

        for doc in docs:
            rels = list(doc.relation_set.all())
            sents = list(doc.entity_set.filter(category__category='Sentence'))

            # map sentence id => sentence start and text

            for sent in sents:
                sentid_sent[sent.id] = (sent.get_start(),sent.get_text())

            for rel in rels:
                args = list(rel.relationargument_set.all())
                ordered_args = []
                rel_sents = set()

                for arg in args:
                    for sent in sents:
                        if arg.get_start() >= sent.start and arg.get_end() <= sent.end:
                            rel_sents.add(sent.id)
                rel_sentids[rel.id] = rel_sents

                for cat in self.argument_order:
                    ordered_arg = [a for a in args if a.category.category == cat]
                    ordered_args.append(ordered_arg[0].argument.text)

                try:
                    direct = rel.relationattribute_set.get(attribute='direct')
                    direct = direct.value
                except RelationAttribute.DoesNotExist:
                    direct = 'U'

                row = (doc.doc_id,)+tuple(ordered_args)

                if row in tuples:
                    if tuples[row][0] != 'D':
                        tuples[row][0] = direct
                else:
                    tuples[row] = [direct,None,None]

                if tuples[row][1] is not None:
                    tuples[row][1].append(str(rel.id))
                else:
                    tuples[row][1] = [str(rel.id)]

                if tuples[row][2] is not None:
                    tuples[row][2] = tuples[row][2].union(rel_sents)
                else:
                    tuples[row][2] = rel_sents

        rows = [row+(attrs[0],','.join(attrs[1]),len(attrs[2]))
                for row,attrs in tuples.items()]

        rows = sorted(rows, key=self.get_row_score, reverse=True)

        self.tuples = rows
        self.sentid_sent = sentid_sent
        self.rel_sentids = rel_sentids
        # pagination
        # self.pages = pages
        self.stat["mirna_length"] = len(set([r[1] for r in rows]))
        self.stat["gene_length"] = len(set([r[2] for r in rows]))
        self.stat["relation_length"] = len(rows)
        self.stat["direct_rel_length"] = len([r for r in rows if r[3] == 'D'])
        self.stat["unknown_rel_length"] = len([r for r in rows if r[3] == 'U'])

        self.request = request
        return super(SearchView, self).get(request)

    def get_row_score(self, row):
        score = 0
        if row[3] == 'D':
            score += 1

        try:
            idx = self.genes.index(row[2].lower())
            score += idx*2 + 2
        except ValueError:
            pass

        return score

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['tuples'] = self.tuples
        context['request'] = self.request
        context['post_url'] = reverse('handle_search')
        context['stat'] = self.stat
        context['query'] = self.query
        context['original_query'] = self.original_query

        # server-side pagination
        # context['pages'] = self.pages

        return context

class DownloadView(SearchView):
    # download function
    view_name = 'download'

    class Echo:
        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value

    def filter_rows(self, rows):
        high_rows = []
        low_rows = []
        gene_file = open('/home/leebird/Dropbox/miRTex paper/use case/tnbc_down_genes.txt','r')
        gene_names = gene_file.read().strip().split('\n')

        for row in rows[1:]:
            if row[0] == '24817091':
                continue
            
            if row[2].upper() in gene_names:
                row = list(row)
                row[2] = row[2].upper()
                high_rows.append(tuple(row))
            else:
                low_rows.append(row)
        high_rows = sorted(high_rows, key=lambda a:a[2])
        return [rows[0]]+high_rows+low_rows



    def get(self, request, query, dtype):
        self.dtype = int(dtype)
        super(DownloadView, self).get(request, query)
        pseudo_buffer = self.Echo()
        writer = csv.writer(pseudo_buffer)

        rows = self.build_rows()

        rows = self.filter_rows(rows)

        response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                         content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="result.csv"'
        return response

    def build_rows(self):
        rows = [('PMID', 'miRNA', 'Gene', 'Directness', 'Sentence')]
        if self.dtype == 1:
            tuples = self.tuples
        elif self.dtype == 2:
            tuples = [row for row in self.tuples if row[3] == 'D']
        elif self.dtype == 3:
            tuples = [row for row in self.tuples if row[3] == 'U']
        else:
            tuples = []

        for row in tuples:
            direct = 'unknown'
            if row[3] == 'D':
                direct = 'direct'

            sents = set()
            for rel_id in row[4].split(','):
                sent_ids = self.rel_sentids[int(rel_id)]
                for sent_id in sent_ids:
                    sents.add(self.sentid_sent[sent_id])

            sents = sorted(list(sents),key=lambda a:a[0])
            sentsText = ' '.join([sent[1] for sent in sents])

            rows.append(row[:3]+(direct,sentsText))

        return rows

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

class GNSearchView(BaseView):
    # search page
    template_name = BaseView.app_name + '/search_gn.html'
    form_class = SearchPubMedForm

    view_name = 'gn_search'
    processor = QueryProcessor()
    page_size = 10
    download = False

    def make_pages(self, page, pmids):
        paginator = Paginator(pmids,self.page_size)

        try:
            current_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            current_page = paginator.page(1)
            page = 1
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            current_page = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        # get page numbers before and after the current page
        prev = page - 2 if page - 2 > 1 else 2
        post = page + 3 if page + 3 < paginator.num_pages else paginator.num_pages

        pages = {'first':1}
        pages['prev'] = range(prev,page) if prev < page else []
        pages['curr'] = page
        pages['post'] = range(page+1,post) if post > page else []
        pages['last'] = paginator.num_pages
        pages['next'] = page + 1 if page+1 < pages['last'] else pages['last']
        pages['before'] = page - 1 if page - 1 > 0 else 1
        return current_page.object_list, pages

    def get(self, request, query):
        pmids = self.processor.get_pmids(query)
        page = request.GET.get('page')
        page = 1 if page is None else int(page)

        self.original_query = query
        self.query = query
        self.genes = self.processor.get_lines(query)
        self.genes.reverse()
        self.stat = {}

        self.stat["pubmed_length"] = len(pmids)

        # all pmids
        docs = list(Document.objects.filter(doc_id__in=pmids))

        # pagintion
        '''
        docs = list(Document.objects.filter(doc_id__in=pmids))
        slide, pages = self.make_pages(page,docs)
        '''

        self.stat["positive_doc_length"] = len(docs)

        # get current page's docs
        # docs = slide

        tuples = []

        for doc in docs:
            entities = list(doc.entity_set.all())

            for entity in entities:
                gid = entity.entityattribute_set.filter(attribute='gid')[0].value
                tuples.append((doc.doc_id,
                               entity.text, 
                              gid))
        print(tuples)

        self.tuples = tuples
        self.request = request
        return super(GNSearchView, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(GNSearchView, self).get_context_data(**kwargs)
        
        context['tuples'] = self.tuples
        context['request'] = self.request
        context['post_url'] = reverse('handle_search')
        context['stat'] = self.stat
        context['query'] = self.query
        context['original_query'] = self.original_query

        # server-side pagination
        # context['pages'] = self.pages
        return context

    def get_row_score(self, row):
        score = 0
        if row[3] == 'D':
            score += 1

        try:
            idx = self.genes.index(row[2].lower())
            score += idx*2 + 2
        except ValueError:
            pass

        return score