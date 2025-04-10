from rest_framework import routers

from identityProviderApp.viewsets import RelyingPartyViewSet


router = routers.DefaultRouter()
router.register(r'client', RelyingPartyViewSet, basename='relyingparty')