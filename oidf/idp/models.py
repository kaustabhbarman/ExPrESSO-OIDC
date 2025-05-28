from django.db import models

# Create your models here.
class IdentityProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hash = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    proving_key_file = models.CharField(max_length=500, blank=True, null=True)
    verification_key_file = models.CharField(max_length=500, blank=True, null=True)
    out_file = models.CharField(max_length=500, blank=True, null=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Identity Provider"
        verbose_name_plural = "Identity Providers"