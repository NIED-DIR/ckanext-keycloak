import logging

import pytest

from ckan.plugins import toolkit as tk

from ckanext.keycloak import helpers


@pytest.fixture(autouse=True)
def clear_button_configuration(monkeypatch):
    for environment_key in (
        'CKANEXT__KEYCLOAK__BUTTON_STYLE',
        'CKANEXT__KEYCLOAK__BUTTON_LABEL',
        'CKANEXT__KEYCLOAK__IDP_HINT',
    ):
        monkeypatch.delenv(environment_key, raising=False)

    for config_key in (
        'ckanext.keycloak.button_style',
        'ckanext.keycloak.button_label',
        'ckanext.keycloak.idp_hint',
    ):
        monkeypatch.delitem(tk.config, config_key, raising=False)

    helpers._warned_button_styles.clear()


def test_default_button():
    assert helpers.keycloak_login_button() == {
        'style': 'default',
        'label': '外部アカウントでログイン',
        'icon': None,
    }


@pytest.mark.parametrize(
    ('style', 'label', 'icon'),
    [
        ('google', 'Googleでログイン', '/icons/keycloak/google.svg'),
        (
            'microsoft',
            'Microsoftでログイン',
            '/icons/keycloak/microsoft.svg',
        ),
        ('github', 'GitHubでログイン', '/icons/keycloak/github.svg'),
        ('gitlab', 'GitLabでログイン', '/icons/keycloak/gitlab.svg'),
    ],
)
def test_supported_button_styles(monkeypatch, style, label, icon):
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.button_style',
        style,
    )

    button = helpers.keycloak_login_button()

    assert button['style'] == style
    assert button['label'] == label
    assert button['icon'] == icon


def test_button_style_is_normalized(monkeypatch):
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.button_style',
        '  MICROSOFT  ',
    )

    assert helpers.keycloak_login_button()['style'] == 'microsoft'


def test_invalid_style_falls_back_to_default(monkeypatch, caplog):
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.button_style',
        'unknown-provider',
    )

    with caplog.at_level(logging.WARNING):
        button = helpers.keycloak_login_button()

    assert button['style'] == 'default'
    assert button['label'] == '外部アカウントでログイン'
    assert 'Unsupported ckanext.keycloak.button_style' in caplog.text


def test_custom_button_label(monkeypatch):
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.button_label',
        'SIP4Dアカウントでログイン',
    )

    assert (
        helpers.keycloak_login_button()['label']
        == 'SIP4Dアカウントでログイン'
    )


def test_empty_custom_label_uses_default(monkeypatch):
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.button_label',
        '   ',
    )

    assert (
        helpers.keycloak_login_button()['label']
        == '外部アカウントでログイン'
    )


def test_environment_variable(monkeypatch):
    monkeypatch.setenv(
        'CKANEXT__KEYCLOAK__BUTTON_STYLE',
        'github',
    )

    assert helpers.keycloak_login_button()['style'] == 'github'


def test_ckan_config_takes_precedence_over_environment(monkeypatch):
    monkeypatch.setenv(
        'CKANEXT__KEYCLOAK__BUTTON_STYLE',
        'github',
    )
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.button_style',
        'google',
    )

    assert helpers.keycloak_login_button()['style'] == 'google'


def test_idp_hint(monkeypatch):
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.idp_hint',
        'google',
    )

    assert helpers.keycloak_idp_hint() == 'google'


def test_empty_idp_hint(monkeypatch):
    monkeypatch.setitem(
        tk.config,
        'ckanext.keycloak.idp_hint',
        '   ',
    )

    assert helpers.keycloak_idp_hint() is None
