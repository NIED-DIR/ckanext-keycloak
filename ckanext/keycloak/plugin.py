import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.keycloak import helpers
from ckanext.keycloak.views import get_blueprint, enable_ckan_internal_login


CONFIG_OPTIONS = (
    'ckanext.keycloak.button_style',
    'ckanext.keycloak.button_label',
    'ckanext.keycloak.idp_hint',
)


class KeycloakPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigDeclaration is available on CKAN 2.10 and later.
    if hasattr(plugins, 'IConfigDeclaration'):
        plugins.implements(plugins.IConfigDeclaration)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'keycloak')

    def get_blueprint(self):
        return get_blueprint()

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'enable_ckan_internal_login': enable_ckan_internal_login,
            'keycloak_login_button': helpers.keycloak_login_button,
        }

    # IConfigDeclaration (CKAN 2.10+)

    def declare_config_options(self, declaration, key):
        for config_key in CONFIG_OPTIONS:
            declaration.declare(config_key)
