#!/bin/bash
source ./agent-vars.sh
AGENT_POD=$(kubectl get pods -n lg-agent --no-headers | awk '{print $1}')
kubectl exec -it $AGENT_POD -n lg-agent -- bash
