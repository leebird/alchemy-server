from django.db import models
from .entity import Entity

class EntityProperty(models.Model):
    class Meta:
        db_table = 'tm_entity_property'

    entity = models.ForeignKey(Entity)
    label = models.CharField(max_length=64)
    value = models.CharField(max_length=128)

    def __str__(self):
        return str((self.entity, self.label, self.value))