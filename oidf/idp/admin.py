from django.contrib import admin

from idp.models import IdentityProvider


# Register your models here.
@admin.register(IdentityProvider)
class IdentityProviderAdmin(admin.ModelAdmin):
    pass