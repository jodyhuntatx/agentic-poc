#!/bin/bash -x

#curl -X POST http://localhost:9000/init

SECRET_ID="data/vault/JodyDemo/K8sSecrets-MySQL/password"
WORKLOAD_ID="ai-agent"

curl -X POST 						\
	-H "Content-Type: application/json"		\
	-d "{						\
		\"secret_id\": \"$SECRET_ID\",		\
		\"workload_id\": \"$WORKLOAD_ID\"	\
	    }"						\
	http://localhost:9000/getsecret
