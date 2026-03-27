# ckanext-keycloak (Customized for SIP4D)

This extension enables CKAN to authenticate users via Keycloak using OpenID Connect (OIDC).

This repository is based on:

- https://github.com/keitaroinc/ckanext-keycloak

## Features

- Keycloak (OIDC) based SSO login for CKAN
- Automatic CKAN user creation on first login
- Support for multiple CKAN instances sharing a single Keycloak server
- Optional disabling of the CKAN internal login form
- Optional SSL verification control for self-signed certificates or development environments
- Designed to be extended for role-based authorization (Keycloak to CKAN)

## Requirements

- CKAN 2.9 or later
- Tested with CKAN 2.10 and 2.11
- Keycloak (OIDC compatible)
- Python 3.x

## Installation

Clone this repository into your CKAN source directory:

```bash
cd /srv/app/src
git clone https://github.com/NIED-DIR/ckanext-keycloak.git
```

Install the extension:

```bash
pip install -e ./ckanext-keycloak
pip install -r ./ckanext-keycloak/requirements.txt
```

Add the plugin to your CKAN configuration:

```ini
ckan.plugins = ... keycloak
```

## Configuration

You can configure the extension via `ckan.ini` or environment variables.

### Required settings

```ini
ckanext.keycloak.server_url = http://<keycloak-host>:8080
ckanext.keycloak.realm_name = <realm>
ckanext.keycloak.client_id = <client-id>
ckanext.keycloak.client_secret_key = <client-secret>
ckanext.keycloak.redirect_uri = https://<ckan-host>/user/sso_login
```

### Environment variable equivalents

```env
CKANEXT__KEYCLOAK__SERVER_URL=http://keycloak.example.com:8080
CKANEXT__KEYCLOAK__REALM_NAME=ckan
CKANEXT__KEYCLOAK__CLIENT_ID=ckan
CKANEXT__KEYCLOAK__CLIENT_SECRET_KEY=xxxxx
CKANEXT__KEYCLOAK__REDIRECT_URI=https://ckan.example.com/user/sso_login
```

## Additional Settings (Custom Extensions)

### 1. Disable CKAN internal login form

```ini
ckanext.keycloak.enable_ckan_internal_login = false
```

Environment variable:

```env
CKANEXT__KEYCLOAK__ENABLE_CKAN_INTERNAL_LOGIN=false
```

- `true`: Show both the CKAN login form and the Keycloak login button
- `false`: Hide the CKAN login form and use Keycloak only

### 2. SSL Verification Control

```ini
ckanext.keycloak.verify_ssl = false
```

Environment variable:

```env
CKANEXT__KEYCLOAK__VERIFY_SSL=false
```

- `true`: Verify SSL certificates. Recommended for production.
- `false`: Disable verification for self-signed certificates or development environments.

## Keycloak Configuration

### Client settings

- Client ID: `ckan`
- Access Type: `confidential`

#### Valid Redirect URIs

```text
https://ckan1.example.com/user/sso_login
https://ckan2.example.com/user/sso_login
```

#### Web Origins

```text
https://ckan1.example.com
https://ckan2.example.com
```

## User Synchronization

This extension uses **Just-In-Time (JIT) provisioning**.

- Users are created in CKAN when they log in via Keycloak.
- No pre-synchronization is required.
- This works with multiple CKAN instances even when they use separate databases.

### Multi-CKAN behavior

| Action | CKAN-A | CKAN-B |
| --- | --- | --- |
| User created in Keycloak | - | - |
| First login to CKAN-A | Created | - |
| First login to CKAN-B | Exists | Created |

## Username Mapping

To ensure consistent users across multiple CKAN instances:

- Use `preferred_username` from Keycloak.
- Avoid using email as the primary key if it may change.

## Authorization (Design Note)

This extension mainly focuses on **authentication**.

Authorization should follow CKAN's standard model:

- Sysadmin (global)
- Organization-based roles:
  - Admin
  - Editor
  - Member

### Recommended Keycloak role naming

```text
ckan_sysadmin
org:<org_name>:admin
org:<org_name>:editor
org:<org_name>:member
```

This extension can be extended to map those Keycloak roles into CKAN permissions.

## Development Notes

### Handling self-signed certificates

Set:

```env
CKANEXT__KEYCLOAK__VERIFY_SSL=false
```

### Debugging

Check CKAN logs:

```bash
docker compose logs ckan | grep keycloak
```

## Known Limitations

- Authorization role synchronization is not fully implemented by default.
- Advanced RBAC requires customization.
- Full internal login disable may require template override depending on CKAN version.

## Future Improvements

- Full Keycloak role to CKAN permission sync
- Organization auto-mapping
- Admin UI integration
- Token refresh handling

## License

Same as the original repository.

## Acknowledgements

Based on:

- https://github.com/keitaroinc/ckanext-keycloak
