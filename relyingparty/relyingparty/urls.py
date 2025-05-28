"""
URL configuration for relyingparty project.

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
import subprocess
import time
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
import requests
from libs.pycrypto.zokrates_pycrypto.babyjubjub import Point
from libs.pycrypto.zokrates_pycrypto.eddsa import PublicKey, PrivateKey
from libs.pycrypto.zokrates_pycrypto.field import FQ

from libs.pycrypto.zokrates_pycrypto.utils import write_signature_for_zokrates_cli
from zok_commands import calculate_hash_file, run_zokrates_command


# get idp from oidf
def get_hash_of_idp(name, retries=2):
    url = f"http://oidf:8000/idp/{name}/"
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            res= response.json()
            ans= get_proving_key_file(res)
            res['matched']=ans
            return res
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    return None



def get_proving_key_file(response_json_data):
    hash= calculate_hash_file(f"{response_json_data['proving_key_file']}")
    if hash==response_json_data['hash']:
        return True
    return False


# get information of a idp currently just 6
# get idp from oidf
def get_registered_replyingparty_by_id(id, retries=2):
    url = f"http://identityprovider:8001/rp/{id}/"
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            res= response.json()
            print(res)
            return res
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    return None

def create_zok_signature_data(rp_data):
    
    public_key= PublicKey(p=Point(x=FQ(int(rp_data['public_key']['x'])), y=FQ(int(rp_data['public_key']['y']))))
    sig = Point(x=rp_data['signature']['sig_x'],y=rp_data['signature']['sig_y']), rp_data['signature']['sig_r']
    msg = hashlib.sha512(rp_data['client_id'].encode("utf-8")).digest()
    idppath = f"/app/zokrates_workspace/rp/{rp_data['id']}"
    if not os.path.isdir(idppath):
        os.makedirs(idppath)
    path= f"/app/zokrates_workspace/rp/{rp_data['id']}/zokrates_inputs.txt"
    write_signature_for_zokrates_cli(public_key, sig, msg, path)

def calculate_witness(oidf_data,rp_data):
        try:
            idppath = f"/app/zokrates_workspace/rp/{rp_data['id']}"
            if not os.path.isdir(idppath):
                os.makedirs(idppath)
            subprocess.run(["cp", oidf_data['out_file'],f"/app/zokrates_workspace/rp/{rp_data['id']}/out"], timeout=5) 
            subprocess.run(["cp", oidf_data['proving_key_file'],f"/app/zokrates_workspace/rp/{rp_data['id']}/proving.key"], timeout=5) 
            subprocess.run(["cp", oidf_data['verification_key_file'],f"/app/zokrates_workspace/rp/{rp_data['id']}/verification.key"], timeout=5) 
            path= f"/app/zokrates_workspace/rp/{rp_data['id']}/zokrates_inputs.txt"
            with open(path, 'r') as file:
                data = file.read()
                d= data.split(" ")
                cmd= ["zokrates", "compute-witness", "-i" ,f"/home/zokrates/zokrates_workspace/rp/{rp_data['id']}/out", "-o", f"/home/zokrates/zokrates_workspace/rp/{rp_data['id']}/witness", "-a"]
                for arg in d:
                    cmd.append(str(arg))
                run_zokrates_command(cmd)
                return data
        except Exception as e:
            return f"Could not load private key: {e}"

def generate_proof(data):
    run_zokrates_command(["zokrates", "generate-proof", 
                          "-w", f"/home/zokrates/zokrates_workspace/rp/{data['id']}/witness",
                          "-i", f"/home/zokrates/zokrates_workspace/rp/{data['id']}/out",
                          "-p", f"/home/zokrates/zokrates_workspace/rp/{data['id']}/proving.key",
                          "-j", f"/home/zokrates/zokrates_workspace/rp/{data['id']}/proof.json"
                          ])
    path= f"/app/zokrates_workspace/rp/{data['id']}/proof.json"
    with open(path, 'r') as file:
        data = json.load(file)

        # Print the data
        print(data)
        return data
def verify_proof(data):
    res= run_zokrates_command(["zokrates", "verify", 
                          "-v", f"/home/zokrates/zokrates_workspace/rp/{data['id']}/verification.key",
                          "-j", f"/home/zokrates/zokrates_workspace/rp/{data['id']}/proof.json"])
    return res



def landing_page(request):

    t0 = time.time()
    response_json_data= get_hash_of_idp("idp1")
    t1 = time.time()
    total1 = t1-t0

    t0 = time.time()
    registered_relying_party= get_registered_replyingparty_by_id(6)
    t1 = time.time()
    total2 = t1-t0

    t0 = time.time()
    create_zok_signature_data(registered_relying_party)
    t1 = time.time()
    total3 = t1-t0

    t0 = time.time()
    calculate_witness(response_json_data,registered_relying_party)
    t1 = time.time()
    total4 = t1-t0

    t0 = time.time()
    proof= generate_proof(registered_relying_party)
    t1 = time.time()
    total5 = t1-t0

    t0 = time.time()
    verify=verify_proof(registered_relying_party)
    t1 = time.time()
    total6 = t1-t0
    return render(request, "landing.html", {"cleint": 0, "json_data": response_json_data, 'r_data':registered_relying_party, 
                                            'proof':proof, "verify":verify,"times":[total1, total2, total3, total4, total5, total6]})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',landing_page, name='landing_page'),
]
