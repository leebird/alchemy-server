from django.db import models
from .document import Document
from .entity_category import EntityCategory


class Entity(models.Model):
    class Meta:
        db_table = 'tm_entity'
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'

    doc = models.ForeignKey(Document, db_index=True)
    category = models.ForeignKey(EntityCategory, db_index=True)
    start = models.IntegerField()
    end = models.IntegerField()
    text = models.TextField()
    uid = models.CharField(max_length=32)

    def get_category(self):
        return self.category.category

    def __str__(self):
        return str((self.doc.doc_id, self.start, self.end, self.text))

    def __repr__(self):
        return self.__str__()