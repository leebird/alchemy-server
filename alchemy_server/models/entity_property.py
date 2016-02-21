from django.db import models
from .entity import Entity

class EntityProperty(models.Model):
    class Meta:
        db_table = 'tm_entity_property'

    # We can store the normalization id
    # here. For example, lable='Entrez' and
    # value='1234'
        
    # The corresponding entity.
    entity = models.ForeignKey(Entity, db_index=True)
    # Property name. 
    label = models.CharField(max_length=64)
    # Property value.
    value = models.CharField(max_length=128)

    def __str__(self):
        return str((self.entity, self.label, self.value))

    def __repr__(self):
        return self.__str__()
