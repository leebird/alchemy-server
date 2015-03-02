from django.contrib import admin
from django_annotation.models import *

# Register your models here.
class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ('doc_id','text')

class RelationAdmin(admin.ModelAdmin):
    search_fields = ['doc__doc_id']
    list_display = ('category','doc_id','argument')

    def argument(self, instance):
        args = instance.relationargument_set.all()
        argStr = [arg.category.category+': '+arg.argument.text for arg in args]
        return ', '.join(argStr)

    def doc_id(self, instance):
        return instance.doc.doc_id

class ArgumentRoleAdmin(admin.ModelAdmin):
    list_display = ('role','relation_category','entity_category')

class ArgumentRoleInline(admin.TabularInline):
    model = ArgumentRole
    extra = 2

class EntityTypeInline(admin.TabularInline):
    model = EntityCategory
    extra = 3

class RelationTypeAdmin(admin.ModelAdmin):
    list_display = ('category','argument_num','arguments')
    inlines = [ArgumentRoleInline]

class EntityAdmin(admin.ModelAdmin):
    list_display = ('doc_id','category','text')

    def doc_id(self, instance):
        return instance.doc.doc_id

    def category(self, instance):
        return instance.category.category

admin.site.register(Document,DocumentAdmin)
admin.site.register(EntityCategory)
admin.site.register(RelationCategory,RelationTypeAdmin)
admin.site.register(ArgumentRole,ArgumentRoleAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Entity, EntityAdmin)
