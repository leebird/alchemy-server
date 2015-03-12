from django.contrib import admin
from django_annotation.models import *
from django.db.models import Count


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ('doc_id', 'text')


class RelationAdmin(admin.ModelAdmin):
    search_fields = ['doc__doc_id']
    list_display = ('category', 'doc_id', 'argument')

    def argument(self, instance):
        args = instance.entity_arguments.all()
        arg_str = [arg.role.role + ': ' + arg.argument.text for arg in args]
        return ', '.join(arg_str)

    def doc_id(self, instance):
        return instance.doc.doc_id


class ArgumentRoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'relation_category')

    def relation_category(self, instance):
        return instance.relation_category.category


class EntityCategoryInline(admin.TabularInline):
    model = EntityCategory
    extra = 3


class EntityCategoryAdmin(admin.ModelAdmin):
    pass


class ArgumentRoleInline(admin.TabularInline):
    model = ArgumentRole
    extra = 2


class RelationCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'arguments')
    inlines = [ArgumentRoleInline]


class EntityAdmin(admin.ModelAdmin):
    list_display = ('doc_id', 'category', 'text')

    def doc_id(self, instance):
        return instance.doc.doc_id

    def category(self, instance):
        return instance.category.category


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection', 'user',
                    'entity_category_num', 'relation_category_num',
                    'timestamp')


    def get_queryset(self, request):
        qs = super(CollectionAdmin, self).get_queryset(request)
        qs = qs.annotate(entity_category_num=Count('entitycategory'))
        qs = qs.annotate(relation_category_num=Count('relationcategory'))
        return qs

    def entity_category_num(self, instance):
        return instance.entity_category_num

    def relation_category_num(self, instance):
        return instance.relation_category_num

    entity_category_num.short_description = 'Entity Category Count'
    relation_category_num.short_description = 'Relation Category Count'


class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)


admin.site.register(Document, DocumentAdmin)
admin.site.register(EntityCategory, EntityCategoryAdmin)
admin.site.register(RelationCategory, RelationCategoryAdmin)
admin.site.register(ArgumentRole, ArgumentRoleAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Collection, CollectionAdmin)
