# Setup logging to new/overwritten logfile with loglevel
import logging
from pathlib import Path

Path("./logs").mkdir(parents=True, exist_ok=True)
logfile = f"./logs/conjursvc.log"
logfmode = 'w'                # w = overwrite, a = append
# Log levels: NOTSET DEBUG INFO WARN ERROR CRITICAL
loglevel = logging.DEBUG
# Cuidado! DEBUG will leak secrets!
logging.basicConfig(filename=logfile, encoding='utf-8', level=loglevel, filemode=logfmode)

#----------------------------------------
# Function to get JWT for authentication
import json
import requests

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

from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

#----------------------------------------
# Get secrets from Conjur
from conjurjwt import ConjurRetrieverJwt
conjurRetriever = None

@app.post("/init")
def init() -> dict:
    conjur_subdomain= "cybr-secrets"
    authn_jwt_id = "agentic"
    workload_id = "ai-agent"

    global conjurRetriever
    conjurRetriever = ConjurRetrieverJwt(conjur_subdomain, authn_jwt_id, jwtProvider_jwtThis)
    return { "conjur_subdomain": conjur_subdomain,
             "authn_jwt_id": authn_jwt_id,
             "workload_id": workload_id,}

class SecretRequest(BaseModel):
  secret_id: str
  workload_id: str

@app.post("/getsecret")
def get_secret(req: SecretRequest) -> str:
    secret = ""
    if conjurRetriever is None:
        logging.error("Conjur retriever was not initialized.")
        raise RuntimeError("Conjur retriever was not initialized.")
    try:
      secret = conjurRetriever.getSecret(req.secret_id, req.workload_id)
    except Exception as e:
      logging.error(e)
    return secret
