

import hashlib
import json
import uuid

from django.core.management import BaseCommand, CommandError

from identityProviderApp.models import KeyValue
from libs.pycrypto.zokrates_pycrypto.eddsa import PrivateKey, PublicKey
from libs.pycrypto.zokrates_pycrypto.field import FQ
from libs.pycrypto.zokrates_pycrypto.utils import write_signature_for_zokrates_cli, to_bytes


class Command(BaseCommand):
    def handle(self, *args, **options):
        raw_msg = "This is my secret message"
        msg = hashlib.sha512(raw_msg.encode("utf-8")).digest()

        # sk = PrivateKey.from_rand()
        # Seeded for debug purpose
        key = FQ(1997011358982923168928344992199991480689546837621580239342656433234255379025)
        sk = PrivateKey(key)
        print(sk.fe.__class__)
        print(sk.fe.n.__class__)
        sig = sk.sign(msg)

        pk = PublicKey.from_private(sk)
        is_verified = pk.verify(sig, msg)
        print(is_verified)