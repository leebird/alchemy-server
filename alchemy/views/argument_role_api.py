from django.views.generic import View
from django_annotation.models import *


class ArgumentRoleAPI(View):
    view_name = 'argument_role_api'

    def get(self, request, argument_role):
        pass

    def post(self, request):
        pass

    @classmethod
    def get_argument_role(cls, role, relation_category):
        try:
            db_role = ArgumentRole.objects.get(role=role, relation_category=relation_category)
        except(ArgumentRole.DoesNotExist, ArgumentRole.MultipleObjectsReturned):
            return False
        else:
            return db_role

    @classmethod
    def save_argument_role(cls, role, relation_category):
        if len(role) == 0:
            return False

        db_role = cls.get_argument_role(role, relation_category)
        if db_role:
            return db_role
        else:
            db_role = ArgumentRole(role=role, relation_category=relation_category)
            db_role.save()
            return db_role