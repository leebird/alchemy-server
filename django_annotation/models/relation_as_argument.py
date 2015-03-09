from django.db import models
from .argument_role import ArgumentRole
from .relation import Relation

class RelationAsArgument(models.Model):
    class Meta:
        db_table = 'tm_relation_as_argument'

    role = models.ForeignKey(ArgumentRole, db_index=True)
    relation = models.ForeignKey(Relation, related_name='relation_arguments', db_index=True)
    argument = models.ForeignKey(Relation, db_index=True)

    def __str__(self):
        return str((self.relation, self.argument, self.category))

    def __repr__(self):
        return self.__str__()