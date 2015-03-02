from django.db import models
from .version import Version

class EntityCategory(models.Model):
    class Meta:
        db_table = 'tm_entity_category'

    category = models.CharField(max_length=32)
    version = models.ForeignKey(Version)

    def __str__(self):
        return self.category