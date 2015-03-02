from django.db import models

class User(models.Model):
    class Meta:
        db_table = 'tm_user'

    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)