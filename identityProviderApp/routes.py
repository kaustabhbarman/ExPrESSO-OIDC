from rest_framework import routers

from identityProviderApp.viewsets import IdentityProviderViewSet


router = routers.DefaultRouter()
router.register(r'identities', IdentityProviderViewSet, basename='relyingparty')