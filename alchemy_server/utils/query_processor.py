import re
from collections import OrderedDict

from alchemy_server.utils.pubmed import PubMedSearcher

class QueryProcessor:

    pat_pmid_query = re.compile(r'[0-9.,;\s]+')
    pat_pmid_list = re.compile(r'[0-9]+')

    def __init__(self):
        pass

    def preprocess(self, query):
        query = query.replace('\r','')
        return query.strip()

    def get_lines(self, query):
        query = self.preprocess(query)
        return list(OrderedDict.fromkeys(query.lower().split('\n')))

    def get_pmids(self, query):
        query = self.preprocess(query)

        if self.pat_pmid_query.match(query):
            return self.match_pmids(query)
        else:
            return self.search_pubmed(query)

    def match_pmids(self, query):
        matched = self.pat_pmid_list.findall(query)
        if matched:
            return matched

    def search_pubmed(self, query):
        searcher = PubMedSearcher()
        return searcher.search(query)
    
