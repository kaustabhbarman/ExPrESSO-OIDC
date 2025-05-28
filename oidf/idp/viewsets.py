import os
import subprocess

from django.core.files import File
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action

from rest_framework.response import Response
from idp.zok_commands import calculate_hash_file, run_zokrates_command
from idp.models import IdentityProvider

# def run_zokrates_setup(proving_path, verification_path):
#     # Step 1: Run ZoKrates setup inside container and capture stdout
#     result = subprocess.run(
#         ["docker", "exec", "zokrates", "/usr/bin/zokrates", "setup"],
#         capture_output=True,
#         text=True
#     )
#     print(result)
#     if result.returncode != 0:
#         print("STDOUT:", result.stdout)
#         print("STDERR:", result.stderr)
#         raise RuntimeError(f"ZoKrates setup failed: {result.stderr or '[no stderr]'}")

#     # Step 2: Save stdout to proving.key
#     with open(proving_path, "w") as f:
#         f.write(result.stdout)

#     # Step 3: Copy verification.key from shared volume (already created by ZoKrates) to your desired location
#     subprocess.run(["cp", "zokrates_workspace/verification.key", verification_path], check=True)

class IdentityProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityProvider
        fields = '__all__'
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }

class IdentityProviderViewSet(viewsets.ModelViewSet):
    queryset = IdentityProvider.objects.all()
    serializer_class = IdentityProviderSerializer
    lookup_field = 'name'


    def create(self, request, *args, **kwargs):
        print("📘 A IDP is about to be registered with data:", request.data)

        # Step 1: Create the instance first
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        try:
            verifier_zok_path= "/home/zokrates/zokrates_workspace/oidf/verifier.zok"
            compile_out_path= f"/home/zokrates/zokrates_workspace/oidf/idp/{instance.pk}/out"
            compile_r1cs_path= f"/home/zokrates/zokrates_workspace/oidf/idp/{instance.pk}/out.r1cs"
            setup_proving_key_path= f"/home/zokrates/zokrates_workspace/oidf/idp/{instance.pk}/proving.key"
            setup_verification_key_path= f"/home/zokrates/zokrates_workspace/oidf/idp/{instance.pk}/verification.key"
            # create needed folder
            idppath = f"/app/zokrates_workspace/oidf/idp/{instance.pk}"
            if not os.path.isdir(idppath):
                os.makedirs(idppath)

            # compile  for given idp
            run_zokrates_command(["zokrates", "compile", "-i",  verifier_zok_path, "-o", compile_out_path, "-r", compile_r1cs_path])
            # setup for given idp
            run_zokrates_command(["zokrates", "setup", "-i",  compile_out_path , "-p" ,setup_proving_key_path, "-v",setup_verification_key_path])
            print(instance)
            idp= IdentityProvider.objects.get(pk=instance.pk)
            print(idp)
            idp.proving_key_file= f"{idppath}/proving.key"
            idp.verification_key_file= f"{idppath}/verification.key"
            idp.out_file=f"{idppath}/out"


            # generate hash fo files
            hash= calculate_hash_file(f"{idppath}/proving.key")
            print(hash)
            idp.hash= hash
            idp.save()
            return Response(self.get_serializer(idp).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

    @action(detail=True, methods=['post'])
    def recreate(self, request, pk=None):
        # TODO: recreate artificat
        pass