from django.db import models
from .user import User


class Version(models.Model):
    class Meta:
        db_table = 'tm_version'

    version = models.CharField(max_length=64)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)