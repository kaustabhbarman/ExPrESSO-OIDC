
import hashlib
import json
import uuid
from django.core.management.base import BaseCommand


from libs.pycrypto.zokrates_pycrypto.eddsa import PrivateKey, PublicKey
from libs.pycrypto.zokrates_pycrypto.field import FQ
from libs.pycrypto.zokrates_pycrypto.utils import write_signature_for_zokrates_cli, to_bytes

class Command(BaseCommand):

    def serialize_signature_for_zokrates(self, pk, sig, msg):
        "Writes the input arguments for verifyEddsa in the ZoKrates stdlib to file."
        sig_R, sig_S = sig
        args = [sig_R.x, sig_R.y, sig_S, pk.p.x.n, pk.p.y.n]
        args = " ".join(map(str, args))

        return args

    def handle(self, *args, **options):
       
        sk = PrivateKey.from_rand()
        pk = PublicKey.from_private(sk)
        print(pk)
        print(sk)
        client_id = hashlib.sha512("002084".encode("utf-8")).digest()
        sig = sk.sign(client_id)

        print(self.serialize_signature_for_zokrates(pk, sig, "002084"))
