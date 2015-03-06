from django.db import models
from .document import Document
from .relation_category import RelationCategory

class Relation(models.Model):
    class Meta:
        db_table = 'tm_relation'

    doc = models.ForeignKey(Document)
    category = models.ForeignKey(RelationCategory)
    uid = models.CharField(max_length=32)
    
    def __str__(self):
        return str(self)