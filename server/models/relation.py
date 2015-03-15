from django.db import models
from .document import Document
from .relation_category import RelationCategory


class Relation(models.Model):
    class Meta:
        db_table = 'tm_relation'

    doc = models.ForeignKey(Document, db_index=True)
    category = models.ForeignKey(RelationCategory, db_index=True)
    uid = models.CharField(max_length=32)

    def __str__(self):
        return str((self.doc.doc_id, self.category))

    def __repr__(self):
        return self.__str__()