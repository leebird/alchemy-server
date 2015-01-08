from urllib import parse, request
import re

class PubMedSearcher:
    eutils = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    pmid_pattern = r'<Id>([0-9]+)</Id>'

    def __init__(self):
        self.fields = {'db': 'pubmed',
                       'retmax': '5000',
                       'term': None}
        
        self.minLength = 3

    def search(self,query):
        query = query.strip()
        if len(query) < self.minLength:
            return None

        query = ' OR '.join(set(query.split('\n')))

        self.fields['term'] = self.restrict_query(query)
        # self.fields['term'] = query
        pairs = self.fields.items()
        url = self.eutils + '?' + parse.urlencode(self.fields)

        response = request.urlopen(url,timeout=10)
        xml = str(response.read())
        pmids = re.findall(self.pmid_pattern,xml)
        #return ['23226300']
        return pmids
                                      
    def restrict_query(self,term):
        tmpl = '({0}) AND (mir[TIAB] OR mirna[TIAB] OR microrna[TIAB])'
        return tmpl.format(term)
