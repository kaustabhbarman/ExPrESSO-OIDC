from rest_framework import serializers

from identityProviderApp.models import RelyingParty


class RelyingPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = RelyingParty
        fields = '__all__'