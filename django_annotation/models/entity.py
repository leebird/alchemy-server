from django.db import models
from .document import Document
from .entity_category import EntityCategory

class Entity(models.Model):
    class Meta:
        db_table = 'tm_entity'

    doc = models.ForeignKey(Document)
    category = models.ForeignKey(EntityCategory)
    start = models.IntegerField()
    end = models.IntegerField()
    text = models.TextField()

    def get_category(self):
        return self.category.category

    def __str__(self):
        return str((self.doc.doc_id, self.start, self.end, self.text))