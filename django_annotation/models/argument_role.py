from django.db import models
from .entity_category import EntityCategory
from .relation_category import RelationCategory

class ArgumentRole(models.Model):
    class Meta:
        db_table = 'tm_argument_role'

    role = models.CharField(max_length=128)
    relation_category = models.ForeignKey(RelationCategory)
    mandatory = models.BooleanField(default=True)

    def __str__(self):
        return self.role

    def __repr__(self):
        return self.__str__()