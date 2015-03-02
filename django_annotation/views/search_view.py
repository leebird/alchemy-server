from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_annotation.models import *
from django_annotation.utils.query_processor import QueryProcessor
from django_annotation.forms import SearchPubMedForm
from .base_view import BaseView

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
                except RelationProperty.DoesNotExist:
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