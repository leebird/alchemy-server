from django.db import models
from .document import Document

class DocumentProperty(models.Model):
    class Meta:
        db_table = 'tm_document_property'

    # The corresponding document.
    doc = models.ForeignKey(Document, db_index=True)
    # Property name.
    label = models.CharField(max_length=64)
    # Property value.
    value = models.CharField(max_length=128)

    def __str__(self):
        return str((self.doc.doc_id, self.label, self.value))

    def __repr__(self):
        return self.__str__()
