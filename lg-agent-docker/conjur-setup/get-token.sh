#!/bin/bash
source ./demo-vars.sh
curl -s	-X POST							\
	-H "Content-Type: application/x-www-form-urlencoded"	\
	-d "workload=$WORKLOAD_ID"				\
	http://localhost:8000/token				\
  | jq -r .access_token
