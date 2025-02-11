#!/bin/bash
source ./demo-vars.sh
PID=$(ps -aux | grep "jwt-this -a $JWT_AUDIENCE" | grep -v grep | awk '{print $2}')
kill -9 $PID
