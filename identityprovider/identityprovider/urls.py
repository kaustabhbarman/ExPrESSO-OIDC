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
from libs.pycrypto.zokrates_pycrypto.babyjubjub import Point
from libs.pycrypto.zokrates_pycrypto.eddsa import PublicKey, PrivateKey
from libs.pycrypto.zokrates_pycrypto.field import FQ

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

#client id 002084 generated via generateenv.py management command
env="15300566248148176359251087857135083433702490185699534455721503897716581654586 1731041133691031814672876691350015875319337371889544898254566634510717581651 20009691480797713157780151153250476165103337718307266577863304399093974841573 12388223396296843178610444897126549579656707086806151712173508413150086990354 902023574817401310148700772379947263210897069942156176345593234473024929067"


def register_client(request, name, **args):
    # env
    # client_id = hashlib.sha512(client_id.encode("utf-8")).digest()
    # pn=5
    # #pn = KeyValue.objects.get(key='PRIVATE').value
    # p= PrivateKey(FQ(int(pn)))
    #sig = p.sign(client_id)

    public_key=PublicKey(p=Point(x=12388223396296843178610444897126549579656707086806151712173508413150086990354, y=902023574817401310148700772379947263210897069942156176345593234473024929067))
    x= public_key.p.x
    y= public_key.p.y
    return JsonResponse({'cleint_id': "002084", 'sig': env, 'public_key_x':x,'public_key_y':y})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path('openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    path('client/<str:name>', register_client)
]
