#!/usr/bin/python3

import json
import logging
import requests
from pathlib import Path

# ConjurRetrieverJwt ============================================
AUTHN_JWT_HEADERS = { "Content-Type": "application/x-www-form-urlencoded",
    		          "Accept-Encoding": "base64"
		            }

class ConjurRetrieverJwt:

  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  #             BEWARE! DEBUG loglevel will leak secrets!
  def __init__(self, cybr_tenant_subdomain, authn_jwt_id,
                jwtProvider, loglevel=logging.INFO):
    self.__private_jwtProvider = jwtProvider
    self.conjur_url = f"https://{cybr_tenant_subdomain}.secretsmgr.cyberark.cloud/api"
    self.conjur_authn_url = f"{self.conjur_url}/authn-jwt/{authn_jwt_id}/conjur/authenticate"
    Path("./logs").mkdir(parents=True, exist_ok=True)
    logfile = f"./logs/conjurJwt-{authn_jwt_id}.log"
    logfmode = 'w'                # w = overwrite, a = append
    logging.basicConfig(filename=logfile, encoding='utf-8', level=loglevel, filemode=logfmode)

  # Private ============================================

  def __private_getJwt(self, workload_id: str) -> str:
    logging.info(f"Getting JWT from IDP for workload ID {workload_id}...")
    
    jwt = self.__private_jwtProvider(workload_id)
    return jwt

  def __private_authnJwt(self, workload_id: str) -> str:
    jwt = self.__private_getJwt(workload_id)
    logging.info("Authenticating to Conjur Cloud...")
    payload = f"jwt={jwt}"
    resp = requests.request("POST", self.conjur_authn_url,
			                headers=AUTHN_JWT_HEADERS, data=payload)
    if resp:
      conjur_token = resp.text
      logging.info("Authentication succeeded.")
      logging.debug(f"Conjur token: {conjur_token}")
    else:
      raise RuntimeError(f"Authentication failed. HTTPS status code: {resp.status_code}")
    return conjur_token

  # Public ============================================

  def getSecret(self, secret_id: str, workload_id: str) -> str:
    conjur_token = self.__private_authnJwt(workload_id)
    logging.info(f"Retrieving secret: {secret_id}")
    secrets_url = f"{self.conjur_url}/secrets/conjur/variable/{secret_id}"
    access_headers = { "Content-Type": "application/json",
        		   "Authorization": f"Token token=\"{conjur_token}\""
		 }
    resp = requests.request("GET", secrets_url, headers=access_headers)
    secret_value = ""
    if resp:
      secret_value = resp.text
      logging.info("Secret retrieved successfully.")
      logging.debug(f"Secret retrieved: {secret_value}")
    else:
        raise RuntimeError(f"Secret retrieval failed. HTTP status code: {resp.status_code}")
    return secret_value 

# End ConjurRetrieverJwt ============================================
