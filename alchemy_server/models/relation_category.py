from django.db import models
from .collection import Collection


class RelationCategory(models.Model):
    class Meta:
        db_table = 'tm_relation_category'
        verbose_name = 'Relation Category'
        verbose_name_plural = 'Relation Categories'
        
    # The entity category, e.g., Gene, miRNA or Disease.
    category = models.CharField(max_length=32)
    # The corresponding collection/text-mining tool that
    # produces this entity category.
    collection = models.ForeignKey(Collection)

    def __str__(self):
        return self.category

    def __repr__(self):
        return self.__str__()

    def arguments(self):
        result = set()
        for role in self.argumentrole_set.all():
            result.add(role.role)
        return ', '.join(result)

    arguments.short_description = 'Arguments'
