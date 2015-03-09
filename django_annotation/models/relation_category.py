from django.db import models
from .version import Version

class RelationCategory(models.Model):
    class Meta:
        db_table = 'tm_relation_category'

    category = models.CharField(max_length=32)
    version = models.ForeignKey(Version)

    def __str__(self):
        return self.category

    def __repr__(self):
        return self.__str__()

    def arguments(self):
        role2entity = {}
        result = []
        for role in self.argumentrole_set.all():
            if role.category in role2entity:
                role2entity[role.category].append(role.entity_category.category)
            else:
                role2entity[role.category] = [role.entity_category.category]
        for category, entity in role2entity.items():
            result.append(category + ':' + '|'.join(entity))
        return ', '.join(result)

    arguments.short_description = 'Arguments'