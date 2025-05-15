from django.conf import settings
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView


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


class ReplyingPartyPage(TemplateView):
    template_name = "relyingparty.html"

class ReplyingPartyWelcomePage(TemplateView):
    template_name = "demo.html"


def userinfo(claims, user):
    claims['name'] = '{0} {1}'.format(user.first_name, user.last_name)
    claims['given_name'] = user.first_name
    claims['family_name'] = user.last_name
    claims['email'] = user.email
    claims['address']['street_address'] = '...'
    return claims