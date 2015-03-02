import re
from django_annotation.utils.pubmed import PubMedSearcher, MedlineParser
from django_annotation.models import Document

class DocumentRetriever:
    """download abstract from pubmed, excluding those already in database
    """
    @classmethod
    def retrieve(cls, pmid_list):
        not_in_db = cls.filter(pmid_list)
        medlines_text = PubMedSearcher.fetch(not_in_db)
        if medlines_text is not None:
            medlines = MedlineParser.parse(medlines_text.strip())

            for pmid, medline in medlines.items():
                title = medline.get('Title')
                abstract = medline.get('Abstract')
                title = title[0] if title is not None else ''
                abstract = abstract[0] if abstract is not None else ''
                text = title + ' ' + abstract
                text = text.strip()
                document = Document(doc_id=pmid, text=text)
                document.save()
        
        return cls.retrieve_db(pmid_list)

    @classmethod
    def retrieve_db(cls, pmid_list):
        documents = Document.objects.filter(doc_id__in=pmid_list)
        doc_text = {}
        for doc in documents:
            doc_text[doc.doc_id] = doc.text
        return doc_text
    
    @classmethod
    def filter(cls, pmid_list):
        documents = Document.objects.filter(doc_id__in=pmid_list)
        in_db = set([doc.doc_id for doc in documents])
        return pmid_list - in_db