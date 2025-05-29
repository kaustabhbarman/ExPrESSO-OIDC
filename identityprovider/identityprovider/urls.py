"""
URL configuration for identityprovider project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import hashlib
import json
import os
import uuid
from django.urls import re_path

from django.contrib.auth.models import User
from rest_framework.decorators import action

from identityproviderapp.views import AuthorizeView
from libs.pycrypto.zokrates_pycrypto.babyjubjub import Point
from libs.pycrypto.zokrates_pycrypto.eddsa import PublicKey, PrivateKey
from libs.pycrypto.zokrates_pycrypto.field import FQ

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import serializers
from oidc_provider.models import Client, ResponseType
from rest_framework import viewsets, mixins


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model= Client
        fields=["id", "name","_redirect_uris"]

class ClientCompleteSerializer(serializers.ModelSerializer):
    public_key = serializers.SerializerMethodField()
    signature = serializers.SerializerMethodField()

    def get_private_key(self, obj):
        try:
            with open('/app/data/keys/private.json', 'r') as file:
                data = json.load(file)
                return data
        except Exception as e:
            return f"Could not load private key: {e}"

    def get_public_key(self, obj):
        try:
            with open('/app/data/keys/public.json', 'r') as file:
                data = json.load(file)
                return data
        except Exception as e:
            return f"Could not load public key: {e}"
    def get_signature(self, obj):
        data=self.get_private_key(obj)
        p = PrivateKey(FQ(int(data["fe"])))
        client_id = hashlib.sha512(obj.client_id.encode("utf-8")).digest()
        sig = p.sign(client_id)
        sig_x= sig[0].x
        sig_y= sig[0].y
        sig_r= sig[1]
        return {"sig_x": str(sig_x), "sig_y": str(sig_y), "sig_r": str(sig_r)}


    class Meta:
        model= Client
        fields=['id', 'name', '_redirect_uris', 'client_id', 'owner', 'response_types', 'public_key','signature']


class ClientCreateViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class=ClientCompleteSerializer
        return super(ClientCreateViewSet, self).retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        raw_msg = uuid.uuid4().hex
        user = User.objects.first()
        return serializer.save(owner=user, client_id=raw_msg, response_types=[2])


router = DefaultRouter()
router.register(r'', ClientCreateViewSet, basename='client')


def get_artifacts(request, pk):
    if os.path.isfile(f"/app/zokrates_workspace/oidf/idp/{pk}/proving.key"):
        return JsonResponse({"id":pk, "proving_key": f"/app/zokrates_workspace/oidf/idp/{pk}/proving.key" , "verification_key": f"/app/zokrates_workspace/oidf/idp/{pk}/verification.key"})
    return JsonResponse({"error": "Artifacts not found"}, status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    re_path("^openid/authorize/?$", AuthorizeView.as_view(), name="authorize"),

    #path("openid/authorize/",AuthorizeView.as_view(), name="authorize"),

    path('openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    #path('client/<str:name>', register_client),
    path('rp/', include(router.urls)),
    path("artifacts/<int:pk>/", get_artifacts ),
]
