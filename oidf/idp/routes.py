from rest_framework import routers

from idp.viewsets import IdentityProviderViewSet

router = routers.DefaultRouter()
router.register(r'', IdentityProviderViewSet, basename='identity_provider')
