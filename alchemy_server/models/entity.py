from django.db import models
from .document import Document
from .entity_category import EntityCategory


class Entity(models.Model):
    class Meta:
        db_table = 'tm_entity'
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'

    # The document that the entity is extracted from.
    doc = models.ForeignKey(Document, db_index=True)
    # The entity category, e.g., Gene, miRNA or Disease.
    category = models.ForeignKey(EntityCategory, db_index=True)
    # The offset of the first character in the document text.
    start = models.IntegerField()
    # The offset of the last character in the document text.
    end = models.IntegerField()
    # The entity text.
    text = models.TextField()
    # The entity id, assigned by the text-mining result reader.
    uid = models.CharField(max_length=32)

    def get_category(self):
        return self.category.category

    def __str__(self):
        return str((self.doc.doc_id, self.start, self.end, self.text))

    def __repr__(self):
        return self.__str__()
