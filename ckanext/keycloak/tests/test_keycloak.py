from urllib.parse import parse_qs, urlsplit

from ckanext.keycloak.keycloak import KeycloakClient


class FakeKeycloakOpenID:
    def auth_url(self, redirect_uri, scope):
        return (
            'https://keycloak.example.com/realms/example/'
            'protocol/openid-connect/auth'
            '?client_id=ckan'
            '&redirect_uri=https%3A%2F%2Fckan.example.com%2Fuser%2Fsso_login'
            '&scope=openid+profile+email'
        )


def create_client(monkeypatch):
    client = KeycloakClient(
        server_url='https://keycloak.example.com',
        client_id='ckan',
        realm_name='example',
        client_secret_key='secret',
    )
    monkeypatch.setattr(
        client,
        'get_keycloak_client',
        lambda: FakeKeycloakOpenID(),
    )
    return client


def test_auth_url_without_idp_hint(monkeypatch):
    client = create_client(monkeypatch)
    auth_url = client.get_auth_url(
        redirect_uri='https://ckan.example.com/user/sso_login',
    )
    query = parse_qs(urlsplit(auth_url).query)

    assert 'kc_idp_hint' not in query


def test_auth_url_with_idp_hint(monkeypatch):
    client = create_client(monkeypatch)
    auth_url = client.get_auth_url(
        redirect_uri='https://ckan.example.com/user/sso_login',
        idp_hint='google',
    )
    query = parse_qs(urlsplit(auth_url).query)

    assert query['kc_idp_hint'] == ['google']
    assert query['client_id'] == ['ckan']
