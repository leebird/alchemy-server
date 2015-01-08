from django.db import models

# Create your models here.

class Document(models.Model):
    doc_id = models.CharField(max_length=30)
    text = models.TextField()

    def __unicode__(self):
        return str((self.doc_id, self.text))

    def __str__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()


class DocumentAtrribute(models.Model):
    doc = models.ForeignKey(Document)
    attribute = models.CharField(max_length=100)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return str((self.doc.doc_id, self.attribute, self.value))


class EntityType(models.Model):
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.category


class RelationType(models.Model):
    category = models.CharField(max_length=100)
    argument_num = models.IntegerField()

    def __unicode__(self):
        return self.category

    def arguments(self):
        res = {}
        resStr = []
        for at in self.argumenttype_set.all():
            if at.category in res:
                res[at.category].append(at.entity_type.category)
            else:
                res[at.category] = [at.entity_type.category]
        for category, entity in res.items():
            resStr.append(category + ':' + '|'.join(entity))
        return ', '.join(resStr)

    arguments.short_description = 'Arguments'


class ArgumentType(models.Model):
    category = models.CharField(max_length=100)
    relation_type = models.ForeignKey(RelationType)
    entity_type = models.ForeignKey(EntityType)
    mandatory = models.BooleanField(default=True)

    def __unicode__(self):
        return self.category


class Entity(models.Model):
    doc = models.ForeignKey(Document)
    category = models.ForeignKey(EntityType)
    start = models.IntegerField()
    end = models.IntegerField()
    text = models.TextField()

    def get_category(self):
        return self.category.category

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_text(self):
        return self.text

    def __unicode__(self):
        return str((self.doc.doc_id, self.start, self.end, self.text))

    def __str__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()


class EntityAttribute(models.Model):
    entity = models.ForeignKey(Entity)
    attribute = models.CharField(max_length=100)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return str((self.entity, self.attribute, self.value))


class Relation(models.Model):
    doc = models.ForeignKey(Document)
    category = models.ForeignKey(RelationType)

    def __unicode__(self):
        return str(self.category)

    def __str__(self):
        return str(self)


class RelationArgument(models.Model):
    category = models.ForeignKey(ArgumentType)
    relation = models.ForeignKey(Relation)
    argument = models.ForeignKey(Entity)

    def get_arg_category(self):
        return self.category.category

    def get_category(self):
        return self.argument.category.category

    def get_start(self):
        return self.argument.start

    def get_end(self):
        return self.argument.end

    def get_text(self):
        return self.argument.text

    def __unicode__(self):
        return str((self.relation, self.argument, self.category))

    def __str__(self):
        return str(self)


class RelationAttribute(models.Model):
    relation = models.ForeignKey(Relation)
    attribute = models.CharField(max_length=100)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return str((self.relation, self.attribute, self.value))

    def __str__(self):
        return str(self)
