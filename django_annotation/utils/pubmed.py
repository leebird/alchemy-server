from urllib import parse, request
import re


class PubMedSearcher(object):
    esearch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    efetch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    minLength = 3

    pmid_pattern = r'<Id>([0-9]+)</Id>'

    def __init__(self):
        pass

    @classmethod
    def fetch(cls, pmid_list):
        if len(pmid_list) == 0:
            return
        
        fields = {'db': 'pubmed',
                  'rettype': 'medline',
                  'retmode': 'text',
                  'id': None}

        if len(pmid_list) == 0:
            return

        pmids = ','.join(pmid_list)
        fields['id'] = pmids
        url = cls.efetch + '?' + parse.urlencode(fields)
        response = request.urlopen(url, timeout=20)
        medlines = response.read().decode('utf-8')
        return medlines

    @classmethod
    def search(cls, query):
        fields = {'db': 'pubmed',
                  'retmax': '5000',
                  'term': None}

        query = query.strip()
        if len(query) < cls.minLength:
            return None

        query = ' OR '.join(set(query.split('\n')))

        fields['term'] = cls.restrict_query(query)
        # self.fields['term'] = query
        url = cls.esearch + '?' + parse.urlencode(fields)

        response = request.urlopen(url, timeout=10)
        xml = response.read().decode('utf-8')
        pmids = re.findall(cls.pmid_pattern, xml)
        # return ['23226300']
        return pmids

    @staticmethod
    def restrict_query(term):
        tmpl = '({0}) AND (mir[TIAB] OR mirna[TIAB] OR microrna[TIAB])'
        return tmpl.format(term)


class MedlineParser(object):
    mapping = {
        "PMID-": "PMID",
        "TI  -": "Title",
        "AB  -": "Abstract",
        "DP  -": "Date",
        "AU  -": "Author",
        "TA  -": "Journal"
    }

    def __init__(self):
        pass

    @classmethod
    def parse(cls, medlines):

        medlines = medlines.replace('\r', '').replace('\n     ', '')
        medline_list = medlines.split('\n\n')

        results = {}
        for block in medline_list:
            medline = {}
            block = block.strip()
            lines = block.split('\n')
            for line in lines:
                head = line[:5]
                if head in cls.mapping:
                    try:
                        medline[cls.mapping[head]].append(line[5:].strip())
                    except KeyError:
                        medline[cls.mapping[head]] = [line[5:].strip()]
            
            if len(medline) > 0:
                results[medline['PMID'][0]] = medline

        return results

    def parse_file(self, filepath):
        pass
    