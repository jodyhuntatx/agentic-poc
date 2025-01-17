#!/usr/bin/python3

import json
import logging
import requests
from conjurjwt import ConjurRetrieverJwt

# function to get JWT from IDP given only a workload ID as parameter
def jwtProvider_jwtThis(workload_id: str) -> str:
  logging.info("IDP is jwt-this on localhost.")
  jwt_issuer_url = "http://localhost:8000/token"
  urlenc_headers= { "Content-Type": "application/x-www-form-urlencoded" }
  payload = f"workload={workload_id}"
  resp_dict = json.loads(requests.request("POST", jwt_issuer_url,
                            headers=urlenc_headers, data=payload).text)
  jwt = ""
  if resp_dict:
    jwt = resp_dict['access_token']
    logging.info("JWT retrieved successfully.")
    logging.debug(f"JWT: {jwt}")
  else:
      raise RuntimeError(f"Error retrieving JWT. Response: {resp_dict}")
  return jwt

# MAIN ================================================
conjur_subdomain= "cybr-secrets"
authn_jwt_id = "agentic"
workload_id = "ai-agent"
secret_id = "data/vault/JodyDemo/Ansible-DBA-MySQL/password"
loglevel = logging.DEBUG

def main():
  conjurRetriever = ConjurRetrieverJwt(conjur_subdomain, authn_jwt_id,
                    jwtProvider_jwtThis, loglevel)
  try:
    secret = conjurRetriever.getSecret(secret_id, workload_id)
    print(secret)
  except Exception as e:
    print(e)

if __name__=="__main__":
  main()
