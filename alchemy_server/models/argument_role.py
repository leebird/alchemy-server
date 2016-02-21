from django.db import models
from .entity_category import EntityCategory
from .relation_category import RelationCategory

class ArgumentRole(models.Model):
    class Meta:
        db_table = 'tm_argument_role'

    # The role of the argument in a relation, e.g., substrate,
    # kinase, agent or theme. Note that this is different from
    # the entity type. For example, if a gene participates in
    # a phosphorylation relation, its role could be kinase or
    # substrate; if it is in a miRNA-target relation, its role
    # could be agent/theme.
    role = models.CharField(max_length=128)

    # The relation category that the role participates.
    relation_category = models.ForeignKey(RelationCategory)

    def __str__(self):
        return self.role

    def __repr__(self):
        return self.__str__()
