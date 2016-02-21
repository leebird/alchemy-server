from django.db import models
from .document import Document
from .relation_category import RelationCategory


class Relation(models.Model):
    class Meta:
        db_table = 'tm_relation'

    # The document that the relation is extracted from.
    doc = models.ForeignKey(Document, db_index=True)
    # The relation category, e.g., phosphorylatio.
    category = models.ForeignKey(RelationCategory, db_index=True)
    # The relation id, assigned by the text-mining result reader.
    uid = models.CharField(max_length=32)

    def __str__(self):
        return str((self.doc.doc_id, self.category))

    def __repr__(self):
        return self.__str__()
