# values used by CLI scripts
unset SELF_HOSTED_PAM
export CYBERARK_EMAIL_DOMAIN=cyberark.cloud.3357
export CYBERARK_IDENTITY_PORTAL_ID=aao4987
export CYBERARK_TENANT_SUBDOMAIN=cybr-secrets
export CYBERARK_IDENTITY_URL=https://${CYBERARK_TENANT_SUBDOMAIN}.cyberark.cloud/api/idadmin
export CYBERARK_CCLOUD_API=https://${CYBERARK_TENANT_SUBDOMAIN}.secretsmgr.cyberark.cloud/api

# Admin - Oauth2 confidential client service user
export CYBERARK_ADMIN_USER=newjodybot@${CYBERARK_EMAIL_DOMAIN}
export CYBERARK_ADMIN_PWD=$(keyring get cybrid newjodybotpwd)

# Authn values
export AUTHN_JWT_ID=agentic
export JWT_POLICY_TEMPLATE=authn-jwt.yml.template
export IDENTITY_PATH=data/$AUTHN_JWT_ID		# Conjur policy path to host identity definition
export TOKEN_APP_PROPERTY=workload		# claim containing name of host identity
export WORKLOAD_ID=ai-agent
export JWT_ISSUER=http://jwt-this
export JWT_AUDIENCE=conjur
export JWT_APP_POLICY_TEMPLATE=app-authn-jwt.yml.template
export JWT_AUTHN_GRANT_POLICY_TEMPLATE=app-authn-grant.yml.template

# Secrets
export JWT_SECRETS_GRANT_POLICY_TEMPLATE=app-secrets-grant.yml.template
export SAFE_NAME=JodyDemo
