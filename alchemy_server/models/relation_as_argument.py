from django.db import models
from .argument_role import ArgumentRole
from .relation import Relation

class RelationAsArgument(models.Model):
    class Meta:
        db_table = 'tm_relation_as_argument'

    # One example of relation-as-argument is ppi-impacted
    # phosphorylation extracted by eFIP. In the relation,
    # two arguments are an interaction between two proteins
    # and a phosphorylation relation. The interaction impacts
    # the phosphorylation relation in some way, e.g., inhibit,
    # block or promote.
        
    # The role that the argument plays in the relation.
    role = models.ForeignKey(ArgumentRole, db_index=True)
    # The relation that the arugment participates.
    relation = models.ForeignKey(Relation, related_name='relation_arguments', db_index=True)
    # The actual relation of the argument.
    argument = models.ForeignKey(Relation, db_index=True)

    def __str__(self):
        return str((self.relation, self.argument, self.category))

    def __repr__(self):
        return self.__str__()
