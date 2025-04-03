from django.db import models

# Create your models here.
class RelyingParty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uid= models.CharField(max_length=255, blank=True)
    redirection_url= models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class KeyValue(models.Model):
    key = models.CharField("Key", max_length=100, unique=True)
    value = models.TextField("Value", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key