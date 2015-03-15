from django.db import models
from .relation import Relation

class RelationProperty(models.Model):
    class Meta:
        db_table = 'tm_relation_property'

    relation = models.ForeignKey(Relation, db_index=True)
    label = models.CharField(max_length=64)
    value = models.CharField(max_length=128)

    def __str__(self):
        return str((self.relation, self.attribute, self.value))

    def __repr__(self):
        return self.__str__()