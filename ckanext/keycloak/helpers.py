import logging
import os
import string
import re
import random
import secrets


import ckan.model as model
import ckan.plugins.toolkit as tk


log = logging.getLogger(__name__)


BUTTON_STYLES = {
    'default': {
        'label': '外部アカウントでログイン',
        'icon': None,
    },
    'google': {
        'label': 'Googleでログイン',
        'icon': '/icons/keycloak/google.svg',
    },
    'microsoft': {
        'label': 'Microsoftでログイン',
        'icon': '/icons/keycloak/microsoft.svg',
    },
    'github': {
        'label': 'GitHubでログイン',
        'icon': '/icons/keycloak/github.svg',
    },
    'gitlab': {
        'label': 'GitLabでログイン',
        'icon': '/icons/keycloak/gitlab.svg',
    },
}

_warned_button_styles = set()


def _config_value(config_key, environment_key, default=None):
    """Read a setting from ckan.ini, then from an environment variable."""
    value = tk.config.get(config_key)

    if value is None:
        value = os.environ.get(environment_key)

    if value is None:
        return default

    return value


def keycloak_login_button():
    """Return the normalized Keycloak login button configuration."""
    raw_style = _config_value(
        'ckanext.keycloak.button_style',
        'CKANEXT__KEYCLOAK__BUTTON_STYLE',
        'default',
    )
    style = str(raw_style or 'default').strip().lower()

    if style not in BUTTON_STYLES:
        if style not in _warned_button_styles:
            log.warning(
                'Unsupported ckanext.keycloak.button_style value "%s". '
                'Falling back to "default". Supported values: %s',
                style,
                ', '.join(sorted(BUTTON_STYLES)),
            )
            _warned_button_styles.add(style)
        style = 'default'

    preset = BUTTON_STYLES[style]
    configured_label = _config_value(
        'ckanext.keycloak.button_label',
        'CKANEXT__KEYCLOAK__BUTTON_LABEL',
    )

    if configured_label is not None:
        configured_label = str(configured_label).strip()

    return {
        'style': style,
        'label': configured_label or preset['label'],
        'icon': preset['icon'],
    }


def keycloak_idp_hint():
    """Return the optional Keycloak identity-provider alias."""
    value = _config_value(
        'ckanext.keycloak.idp_hint',
        'CKANEXT__KEYCLOAK__IDP_HINT',
    )

    if value is None:
        return None

    value = str(value).strip()
    return value or None


def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))


def ensure_unique_username_from_email(email):
    localpart = email.split('@')[0]
    cleaned_localpart = re.sub(r'[^\w]', '-', localpart).lower()

    if not model.User.get(cleaned_localpart):
        return cleaned_localpart

    max_name_creation_attempts = 10

    for _ in range(max_name_creation_attempts):
        random_number = random.SystemRandom().random() * 10000
        name = '%s-%d' % (cleaned_localpart, random_number)
        if not model.User.get(name):
            return name

    return cleaned_localpart


def process_user(userinfo):
    return _get_user_by_email(userinfo.get('email')) or _create_user(userinfo)


def _get_user_by_email(email):
    user = model.User.by_email(email)
    if user and isinstance(user, list):
        user = user[0]

    activate_user_if_deleted(user)
    
    return user


def activate_user_if_deleted(user):
    u'''Reactivates deleted user.'''
    if not user:
        return
    if user.is_deleted():
        user.activate()
        user.commit()
        log.info(u'User {} reactivated'.format(user.name))


def _create_user(userinfo):
    context = {
        u'ignore_auth': True,
    }
    created_user_dict = tk.get_action(
        u'user_create'
    )(context, userinfo)
    
    return _get_user_by_email(created_user_dict['email'])
