#!/bin/bash
set -eou pipefail

source ./demo-vars.sh

#################
main() {
  configure_authn_jwt
  set_authn_jwt_variables
  ./ccloud-cli.sh enable authn-jwt $AUTHN_JWT_ID
  ./ccloud-cli.sh status authn-jwt $AUTHN_JWT_ID
}

###################################
configure_authn_jwt() {
  echo "Initializing Conjur JWT authentication policy..."
  mkdir -p ./policy
  cat ./templates/$JWT_POLICY_TEMPLATE				\
  | sed -e "s#{{ AUTHN_JWT_ID }}#$AUTHN_JWT_ID#g"		\
  > ./policy/$JWT_POLICY_TEMPLATE
  ./ccloud-cli.sh append /conjur/authn-jwt ./policy/$JWT_POLICY_TEMPLATE
}

############################
set_authn_jwt_variables() {
  # Get signing keys from K8s cluster
  JWT_KEYS=$(kubectl get --raw /openid/v1/jwks)
  echo "Initializing Conjur JWT authentication variables..."
  ./ccloud-cli.sh set conjur/authn-jwt/$AUTHN_JWT_ID/audience $JWT_AUDIENCE
  ./ccloud-cli.sh set conjur/authn-jwt/$AUTHN_JWT_ID/issuer $JWT_ISSUER
  ./ccloud-cli.sh set conjur/authn-jwt/$AUTHN_JWT_ID/public-keys "{\"type\":\"jwks\", \"value\": $JWT_KEYS }"
   echo "Enabling authn-jwt/$AUTHN_JWT_ID endpoint..."
  ./ccloud-cli.sh set conjur/authn-jwt/$AUTHN_JWT_ID/token-app-property $TOKEN_APP_PROPERTY
   echo "Checking endpoint status..."
  ./ccloud-cli.sh set conjur/authn-jwt/$AUTHN_JWT_ID/identity-path $IDENTITY_PATH
}

main "$@"
