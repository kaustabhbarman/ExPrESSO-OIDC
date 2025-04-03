import hashlib
import json
import uuid

from django.core.management import BaseCommand, CommandError

from identityProviderApp.models import KeyValue
from libs.pycrypto.zokrates_pycrypto.eddsa import PrivateKey, PublicKey
from libs.pycrypto.zokrates_pycrypto.field import FQ
from libs.pycrypto.zokrates_pycrypto.utils import write_signature_for_zokrates_cli, to_bytes


class Command(BaseCommand):

    def serialize_signature_for_zokrates(self, pk, sig, msg):
        "Writes the input arguments for verifyEddsa in the ZoKrates stdlib to file."
        sig_R, sig_S = sig
        args = [sig_R.x, sig_R.y, sig_S, pk.p.x.n, pk.p.y.n]
        args = " ".join(map(str, args))

        # M0 = msg.hex()[:64]
        # M1 = msg.hex()[64:]
        # b0 = [str(int(M0[i:i + 8], 16)) for i in range(0, len(M0), 8)]
        # b1 = [str(int(M1[i:i + 8], 16)) for i in range(0, len(M1), 8)]
        # args = args #+ " " #+ " ".join(b0 + b1)

        return args

    def handle(self, *args, **options):
        # sk = PrivateKey.from_rand()
        # pk = PublicKey.from_private(sk)
        # self.stdout.write(
        #     self.style.SUCCESS('private key: {}'.format(sk))
        # )
        # self.stdout.write(
        #     self.style.SUCCESS('public key: {}'.format(pk))
        # )
        # path = '.env.txt'
        # with open(path, "w") as text_file:
        #     text_file.write("PRIVATE_KEY={}\n".format(sk.fe))
        #     text_file.write("PUBLIC_KEY={}\n".format(pk.p))
        # self.stdout.write(
        #     self.style.SUCCESS('env successfully created')
        # )

        #raw_msg = uuid.uuid4().hex
        #print(raw_msg)
        #cleint_id = hashlib.sha512(raw_msg.encode("utf-8")).digest()

        # sk = PrivateKey.from_rand()
        # Seeded for debug purpose
        #key = FQ(1997011358982923168928344992199991480689546837621580239342656433234255379025)
        sk = PrivateKey.from_rand()
        #sig = sk.sign(cleint_id)

        pk = PublicKey.from_private(sk)

        #print(self.serialize_signature_for_zokrates(pk, sig, cleint_id))
        # privateObj, created = KeyValue.objects.update_or_create(
        #     #key= 'PRIVATE',value= to_bytes(sk)
        #     #key = 'PRIVATE', value = sk
        #     key= 'PRIVATE', value= sk.fe #repr(sk)#json.dump({"fe": sk.fe})
        # )
        privateObj, created = KeyValue.objects.update_or_create(
            #key= 'PRIVATE',value= to_bytes(sk)
            #key = 'PRIVATE', value = sk
            key= 'PRIVATE', value= sk.fe.n #repr(sk)#json.dump({"fe": sk.fe})
        )
        publicObj, created = KeyValue.objects.update_or_create(
            key='PUBLIC', value= pk.p #repr(pk) # json.dump({"p": pk.p})
            #key = 'PUBLIC', value = pk
        )

        # zokObj, created = KeyValue.objects.update_or_create(
        #     key='ZOKSERIALIZED', value=str(self.serialize_signature_for_zokrates(pk, sig, cleint_id))
        # )

