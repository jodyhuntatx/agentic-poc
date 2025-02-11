#!/usr/bin/python3
import json
import sys
import logging
import requests
from pathlib import Path

Path("./logs").mkdir(parents=True, exist_ok=True)
logfile = "./logs/authn-workload.log"
logfmode = 'w'                # w = overwrite, a = append

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
loglevel = logging.DEBUG
# BEWARE! DEBUG loglevel will leak secrets!

# Constants ============================================
WORKLOAD_ID = "ai-agent"
JWT_ISSUER_URL = "http://localhost:8000/token"
CYBERARK_TENANT_SUBDOMAIN = "cybr-secrets"
CONJUR_URL = f"https://{CYBERARK_TENANT_SUBDOMAIN}.secretsmgr.cyberark.cloud/api"
AUTHN_JWT_ID = "agentic"
URLENC_HEADERS = { "Content-Type": "application/x-www-form-urlencoded" }
AUTHN_JWT_HEADERS = { "Content-Type": "application/x-www-form-urlencoded",
    		      "Accept-Encoding": "base64"
		    }

# MAIN =================================================
logging.basicConfig(filename=logfile, encoding='utf-8', level=loglevel, filemode=logfmode)

logging.info("Getting JWT from IDP...")
payload = f"workload={WORKLOAD_ID}"
resp_dict = json.loads(requests.request("POST", JWT_ISSUER_URL,
			headers=URLENC_HEADERS, data=payload).text)
if resp_dict:
  JWT = resp_dict['access_token']
  logging.info("JWT retrieved successfully.")
  logging.debug(f"JWT: {JWT}")
else:
  logging.error("Error retrieving JWT", resp_dict)
  sys.exit(-1)

logging.info("Authenticating to Conjur Cloud...")
CONJUR_AUTHN_URL = f"{CONJUR_URL}/authn-jwt/{AUTHN_JWT_ID}/conjur/authenticate"
payload = f"jwt={JWT}"
resp = requests.request("POST", CONJUR_AUTHN_URL,
			headers=AUTHN_JWT_HEADERS, data=payload)
if resp:
  conjur_token = resp.text
  logging.info("Authentication succeeded.")
  logging.debug(f"Conjur token: {conjur_token}")
else:
  logging.error("Authentication failed:", resp.status_code)
  sys.exit(-1)

var_id = "data/vault/JodyDemo/Ansible-DBA-MySQL/password"
logging.info(f"Retrieving secret: {var_id}")
SECRETS_ENDPOINT = f"{CONJUR_URL}/secrets/conjur/variable/{var_id}"
ACCESS_HEADERS = { "Content-Type": "application/json",
    		   "Authorization": f"Token token=\"{conjur_token}\""
		 }
resp = requests.request("GET", SECRETS_ENDPOINT,
		headers=ACCESS_HEADERS)
if resp:
  var_value = resp.text
  logging.info("Secret retrieved successfully.")
  logging.debug(f"Secret retrieved: {var_value}")
else:
  logging.error("Retrieval failed:", resp.status_code)
