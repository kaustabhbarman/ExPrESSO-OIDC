import hashlib
import json
import pickle
import uuid
from pickle import FALSE

from charset_normalizer import from_bytes
from django.http import FileResponse, Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

from identityProviderApp.authentication import CsrfExemptSessionAuthentication
from identityProviderApp.models import RelyingParty, KeyValue
from identityProviderApp.serializers import RelyingPartySerializer
from libs.pycrypto.zokrates_pycrypto.babyjubjub import Point
from libs.pycrypto.zokrates_pycrypto.eddsa import PublicKey, PrivateKey
from libs.pycrypto.zokrates_pycrypto.field import FQ


# ViewSets define the view behavior.
class IdentityProviderViewSet(viewsets.ModelViewSet):
    queryset = RelyingParty.objects.all()
    serializer_class = RelyingPartySerializer
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @action(detail=False, methods=['get'], url_path='download-file', name='df')
    def proving_key_url(self,request, pk=None):
        try:
            file_handle = open('proving.key', 'rb')  # ✅ Keep file open
            response = FileResponse(file_handle, as_attachment=True)
            return response
        except FileNotFoundError:
            raise Http404

    def create(self, request, *args, **kwargs):
        # Deserialize the request data
        raw_msg = uuid.uuid4().hex
        client_id = hashlib.sha512(raw_msg.encode("utf-8")).digest()

        request.data['uid'] = str(raw_msg)
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        Point.generator()
        #headers = self.get_success_headers(serializer.data)
        public_key=KeyValue.objects.get(key='PUBLIC').value
        pn = KeyValue.objects.get(key='PRIVATE').value
        p= PrivateKey(FQ(int(pn)))

        print(p)
        # create client id

        sig = p.sign(client_id)

        print("Cleint ID: ", raw_msg)
        print("Public Key: ", public_key)
        print("Signature: ", sig)
        print("Proving Key: ", self.proving_key_url(request, *args, **kwargs))
        #"proving_key":reverse('relyingparty-df', kwargs={'pk': 1})
        res={"client_id":str(raw_msg),"public_key":str(public_key),"signature":str(sig), }
        return Response(res, status=status.HTTP_201_CREATED)

