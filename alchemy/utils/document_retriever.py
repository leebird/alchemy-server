import re
from django_annotation.utils.pubmed import PubMedSearcher, MedlineParser


class DocumentRetriever:
    @classmethod
    def retrieve(cls, pmid_list):
        medlines_text = PubMedSearcher.fetch(pmid_list)
        medlines = MedlineParser.parse(medlines_text.strip())
        return medlines