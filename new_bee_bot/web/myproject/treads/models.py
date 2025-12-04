from django.db import models


class History(models.Model):
    id_tread = models.CharField(max_length=255)
    created_at = models.DateTimeField()
