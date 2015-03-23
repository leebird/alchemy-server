from django.contrib import admin
from alchemy_server.models import *
from django.db.models import Count


class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('collection', 'user',
                    'entity_category_count', 'relation_category_count',
                    'timestamp')


    def get_queryset(self, request):
        qs = super(CollectionAdmin, self).get_queryset(request)
        qs = qs.annotate(entity_category_count=Count('entitycategory', distinct=True))
        qs = qs.annotate(relation_category_count=Count('relationcategory', distinct=True))
        return qs

    def entity_category_count(self, instance):
        return instance.entity_category_count

    def relation_category_count(self, instance):
        return instance.relation_category_count

    entity_category_count.short_description = 'Entity Category Count'
    relation_category_count.short_description = 'Relation Category Count'


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ('doc_id', 'text')


class ArgumentRoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'relation_category')

    def relation_category(self, instance):
        return instance.relation_category.category


class EntityCategoryAdmin(admin.ModelAdmin):
    list_select_related = ()
    list_display = ('category', 'entity_count', 'collection_name', 'user' )

    def user(self, instance):
        return instance.collection.user.username

    def collection_name(self, instance):
        return instance.collection.collection

    collection_name.short_description = 'Collection'

    def entity_count(self, instance):
        return instance.entity_count

    entity_count.short_description = 'Entity Count'

    def get_queryset(self, request):
        qs = super(EntityCategoryAdmin, self).get_queryset(request)
        qs = qs.annotate(entity_count=Count('entity', distinct=True))
        return qs


class RelationCategoryAdmin(admin.ModelAdmin):
    list_select_related = ()
    list_display = ('category', 'arguments', 'relation_count', 'collection_name', 'user')

    def user(self, instance):
        return instance.collection.user.username

    def collection_name(self, instance):
        return instance.collection.collection

    collection_name.short_description = 'Collection'

    def relation_count(self, instance):
        return instance.relation_count

    relation_count.short_description = 'Relation Count'

    def get_queryset(self, request):
        qs = super(RelationCategoryAdmin, self).get_queryset(request)
        qs = qs.annotate(relation_count=Count('relation', distinct=True))
        return qs


class EntityAdmin(admin.ModelAdmin):
    list_select_related = ()
    list_display = ('doc_id_', 'category', 'text')

    def doc_id_(self, instance):
        return instance.doc.doc_id

    def category(self, instance):
        return instance.category.category


class RelationAdmin(admin.ModelAdmin):
    list_select_related = ()
    search_fields = ['doc__doc_id']
    list_display = ('category', 'doc_id_', 'argument')

    def argument(self, instance):
        args = instance.entity_arguments.all()
        arg_str = [arg.role.role + ': ' + arg.argument.text for arg in args]
        return ', '.join(arg_str)

    def doc_id_(self, instance):
        return instance.doc.doc_id


admin.site.register(Document, DocumentAdmin)
admin.site.register(EntityCategory, EntityCategoryAdmin)
admin.site.register(RelationCategory, RelationCategoryAdmin)
admin.site.register(ArgumentRole, ArgumentRoleAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Collection, CollectionAdmin)
