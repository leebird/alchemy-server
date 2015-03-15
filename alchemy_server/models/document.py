from django.db import models

class Document(models.Model):
    class Meta:
        db_table = 'tm_document'

    doc_id = models.CharField(max_length=32, db_index=True)
    text = models.TextField()

    def __str__(self):
        return str((self.doc_id, self.text))

    def __repr__(self):
        return self.__str__()