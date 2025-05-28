"""
URL configuration for oidf project.

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
import subprocess
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.urls import path, include
import hashlib
import os

from idp.routes import router
from oidf.settings import BASE_DIR

def get_sha256_hash(file_path):
    hash_sha256 = hashlib.sha256() 
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def get_verifier_zok(request):
    return JsonResponse({"verifier": "zok"})

def get_client_hash_by_name(request, name):
    return JsonResponse({"name": str(name)})

def get_client_hash_by_id(request, id):
    p_file= os.path.join(BASE_DIR,'proving.key')
    v_file= os.path.join(BASE_DIR,'verification.key')
    print(p_file)
    hash_proving_key= get_sha256_hash(p_file)
    hash_verification_key= get_sha256_hash(v_file)

    print(hash_proving_key)
    print(hash_verification_key)
    return JsonResponse({"id": str(id), 'p_hash':hash_proving_key, 'v_hash': hash_verification_key})

def create_client_artifact_by_name(request, name):
    return JsonResponse({"artificate": str(name)})

def run_bash_script(request):
    p = subprocess.Popen("ls -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    print(p)
    return JsonResponse({'res':str(p)})




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path("state/",get_verifier_zok),
    path("hash/<int:id>/",get_client_hash_by_id),
    path("hash/<str:name>/",get_client_hash_by_name),
    path("artificat/<str:name>/",create_client_artifact_by_name),
    path('idp/', include((router.urls,'identityProvider'), namespace='idp')),
    path("bash/", run_bash_script)

]
