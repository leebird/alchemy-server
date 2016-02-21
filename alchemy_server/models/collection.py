from django.db import models
from .user import User


class Collection(models.Model):
    class Meta:
        db_table = 'tm_collection'

    # The name of the text-mining tool, e.g., RLIMS-P, miRTex.
    collection = models.CharField(max_length=64, db_index=True)
    # The corresponding user.
    user = models.ForeignKey(User, db_index=True)
    # An automatically created timestamp.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # __str__ must return type str
        return str((self.user.username, self.collection))
    
    def __repr__(self):
        return self.__str__()
