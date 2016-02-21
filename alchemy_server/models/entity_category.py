from django.db import models
from .collection import Collection

class EntityCategory(models.Model):
    class Meta:
        db_table = 'tm_entity_category'
        verbose_name = 'Entity Category'
        verbose_name_plural = 'Entity Categories'

    # The entity category, e.g., Gene, miRNA or Disease.
    category = models.CharField(max_length=32)
    # The corresponding collection/text-mining tool that
    # produces this entity category.
    collection = models.ForeignKey(Collection)

    def __str__(self):
        return self.category

    def __repr__(self):
        return self.__str__()
