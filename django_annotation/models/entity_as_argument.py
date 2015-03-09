from django.db import models
from .argument_role import ArgumentRole
from .relation import Relation
from .entity import Entity

class EntityAsArgument(models.Model):
    class Meta:
        db_table = 'tm_entity_as_argument'

    role = models.ForeignKey(ArgumentRole)
    relation = models.ForeignKey(Relation, related_name='entity_arguments')
    argument = models.ForeignKey(Entity)

    def __str__(self):
        return str((self.relation, self.argument, self.category))

    def __repr__(self):
        return self.__str__()