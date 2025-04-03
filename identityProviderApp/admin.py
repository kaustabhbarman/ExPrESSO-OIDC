from django.contrib import admin

from identityProviderApp.models import RelyingParty, KeyValue


# Register your models here.
@admin.register(RelyingParty)
class RelyingPartyAdmin(admin.ModelAdmin):
    pass


@admin.register(KeyValue)
class KeyValueAdmin(admin.ModelAdmin):
    list_display = ["key", "value", "created_at", "updated_at"]