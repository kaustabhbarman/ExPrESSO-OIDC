import json
import os
import time
from enum import verify

import requests
from django.conf import settings
from django.contrib.auth.views import LoginView, redirect_to_login
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from oidc_provider.compat import get_attr_or_callable
from oidc_provider.lib.endpoints.authorize import AuthorizeEndpoint
from oidc_provider.lib.errors import AuthorizeError, ClientIdError, RedirectUriError
from django.contrib.auth import logout as django_user_logout
from oidc_provider.lib.utils.authorize import strip_prompt_login
from oidc_provider.lib.utils.common import redirect
from oidc_provider.models import Client
from oidc_provider.views import OIDC_TEMPLATES
from oidc_provider import settings, signals

from identityproviderapp.zok_commands import run_zokrates_command


# Create your views here.
def idp_after_userlogin_hook(request, user, client):
    print("-------------------------")
    print(request)
    print(user)
    print(client)
    print("-------------------------")
    return None


class CustomLoginView(LoginView):

    def get_redirect_url(self):
        if self.request.user.is_authenticated:
            client = self.request.user.oidc_clients_set.all().first()
            print(client.client_id, " ")
            print(client.redirect_uris)
            uri= f'/openid/authorize/?client_id={client.client_id}&redirect_uri={client.redirect_uris[0]}'
            redirect_to= uri
        else:
            redirect_to = settings.LOGIN_REDIRECT_URL
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""

def userinfo(claims, user):
    claims['name'] = '{0} {1}'.format(user.first_name, user.last_name)
    claims['given_name'] = user.first_name
    claims['family_name'] = user.last_name
    claims['email'] = user.email
    claims['address']['street_address'] = '...'
    return claims


def get_idp_from_oidf(name, retries=2):
    url = f"http://oidf:8000/idp/{name}/"
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            res= response.json()
            return res
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)
    return None


def save_json_to_file(json_string, folder_path, filename):
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Parse the JSON string to ensure it's valid
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return

    # Construct full path
    file_path = os.path.join(folder_path, filename)

    # Write JSON to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)


    print(f"✅ JSON saved to {file_path}")


# # Example usage
# json_data = '{"name": "Alice", "age": 30, "city": "Berlin"}'
# folder = 'output/data'
# file_name = 'user_profile.json'
#
# save_json_to_file(json_data, folder, file_name)


class AuthorizeView(View):
    authorize_endpoint_class = AuthorizeEndpoint

    def verify_proof(self, proof, id):
        res = run_zokrates_command(["zokrates", "verify",
                                    "-v", f"/home/zokrates/zokrates_workspace/oidf/idp/{id}/verification.key",
                                    "-j", proof])
        return res


    def get(self, request, *args, **kwargs):
        print("AuthorizeView GET method called")
        proof = request.GET.get('proof')
        try:
            data = get_idp_from_oidf("idp1")
            print(data)
            save_json_to_file(proof, f"/app/zokrates_workspace/idp/{data['id']}", "proof.json")
            if self.verify_proof(f"/home/zokrates/zokrates_workspace/idp/{data['id']}/proof.json", data['id']):
                print("Proof verified")
                pass

            else:
                raise Exception("Proof not valid")
        except Exception as e:
            context = {
                "error": "Proof verification failed",
                "description": "Proof verification failed. Please ensure you have provided a valid proof.",
            }
            return render(request, OIDC_TEMPLATES["error"], context)

        print(proof)
        authorize = self.authorize_endpoint_class(request)
        try:
            authorize.validate_params()

            if get_attr_or_callable(request.user, "is_authenticated"):
                # Check if there's a hook setted.
                hook_resp = settings.get("OIDC_AFTER_USERLOGIN_HOOK", import_str=True)(
                    request=request, user=request.user, client=authorize.client
                )
                if hook_resp:
                    return hook_resp

                if "login" in authorize.params["prompt"]:
                    if "none" in authorize.params["prompt"]:
                        raise AuthorizeError(
                            authorize.params["redirect_uri"], "login_required", authorize.grant_type
                        )
                    else:
                        django_user_logout(request)
                        next_page = strip_prompt_login(request.get_full_path())
                        return redirect_to_login(next_page, settings.get("OIDC_LOGIN_URL"))

                if "select_account" in authorize.params["prompt"]:
                    # TODO: see how we can support multiple accounts for the end-user.
                    if "none" in authorize.params["prompt"]:
                        raise AuthorizeError(
                            authorize.params["redirect_uri"],
                            "account_selection_required",
                            authorize.grant_type,
                        )
                    else:
                        django_user_logout(request)
                        return redirect_to_login(
                            request.get_full_path(), settings.get("OIDC_LOGIN_URL")
                        )

                if {"none", "consent"}.issubset(authorize.params["prompt"]):
                    raise AuthorizeError(
                        authorize.params["redirect_uri"], "consent_required", authorize.grant_type
                    )

                if not authorize.client.require_consent and (
                    authorize.is_client_allowed_to_skip_consent()
                    and "consent" not in authorize.params["prompt"]
                ):
                    return redirect(authorize.create_response_uri())

                if authorize.client.reuse_consent:
                    # Check if user previously give consent.
                    if authorize.client_has_user_consent() and (
                        authorize.is_client_allowed_to_skip_consent()
                        and "consent" not in authorize.params["prompt"]
                    ):
                        return redirect(authorize.create_response_uri())

                if "none" in authorize.params["prompt"]:
                    raise AuthorizeError(
                        authorize.params["redirect_uri"], "consent_required", authorize.grant_type
                    )

                # Generate hidden inputs for the form.
                context = {
                    "params": authorize.params,
                }
                hidden_inputs = render_to_string("oidc_provider/hidden_inputs.html", context)

                # Remove `openid` from scope list
                # since we don't need to print it.
                if "openid" in authorize.params["scope"]:
                    authorize.params["scope"].remove("openid")

                context = {
                    "client": authorize.client,
                    "hidden_inputs": hidden_inputs,
                    "params": authorize.params,
                    "scopes": authorize.get_scopes_information(),
                }

                return render(request, OIDC_TEMPLATES["authorize"], context)
            else:
                if "none" in authorize.params["prompt"]:
                    raise AuthorizeError(
                        authorize.params["redirect_uri"], "login_required", authorize.grant_type
                    )
                if "login" in authorize.params["prompt"]:
                    next_page = strip_prompt_login(request.get_full_path())
                    return redirect_to_login(next_page, settings.get("OIDC_LOGIN_URL"))

                return redirect_to_login(request.get_full_path(), settings.get("OIDC_LOGIN_URL"))

        except (ClientIdError, RedirectUriError) as error:
            context = {
                "error": error.error,
                "description": error.description,
            }

            return render(request, OIDC_TEMPLATES["error"], context)

        except AuthorizeError as error:
            uri = error.create_uri(authorize.params["redirect_uri"], authorize.params["state"])

            return redirect(uri)

    def post(self, request, *args, **kwargs):
        authorize = self.authorize_endpoint_class(request)

        try:
            authorize.validate_params()

            if not request.POST.get("allow"):
                signals.user_decline_consent.send(
                    self.__class__,
                    user=request.user,
                    client=authorize.client,
                    scope=authorize.params["scope"],
                )

                raise AuthorizeError(
                    authorize.params["redirect_uri"], "access_denied", authorize.grant_type
                )

            signals.user_accept_consent.send(
                self.__class__,
                user=request.user,
                client=authorize.client,
                scope=authorize.params["scope"],
            )

            # Save the user consent given to the client.
            authorize.set_client_user_consent()

            uri = authorize.create_response_uri()

            return redirect(uri)

        except AuthorizeError as error:
            uri = error.create_uri(authorize.params["redirect_uri"], authorize.params["state"])

            return redirect(uri)

