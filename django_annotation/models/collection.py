from django.db import models
from .user import User


class Collection(models.Model):
    class Meta:
        db_table = 'tm_collection'

    collection = models.CharField(max_length=64, db_index=True)
    user = models.ForeignKey(User, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # __str__ must return type str
        return str((self.user.username, self.collection))
    
    def __repr__(self):
        return self.__str__()