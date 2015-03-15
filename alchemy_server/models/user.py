from django.db import models

class User(models.Model):
    class Meta:
        db_table = 'tm_user'

    username = models.CharField(max_length=32, db_index=True)
    password = models.CharField(max_length=32, db_index=True)
    
    def __str__(self):
        return self.username

    def __repr__(self):
        return self.__str__()