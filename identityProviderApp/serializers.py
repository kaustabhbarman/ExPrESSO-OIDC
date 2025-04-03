from rest_framework import serializers

from identityProviderApp.models import RelyingParty


class RelyingPartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RelyingParty
        fields = '__all__'