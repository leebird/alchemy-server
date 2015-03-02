from django.db import models
from .argument_role import ArgumentRole
from .relation import Relation

class RelationAsArgument(models.Model):
    class Meta:
        db_table = 'tm_relation_as_argument'

    category = models.ForeignKey(ArgumentRole)
    relation = models.ForeignKey(Relation, related_name='relation_arguments')
    argument = models.ForeignKey(Relation)

    def __str__(self):
        return str((self.relation, self.argument, self.category))