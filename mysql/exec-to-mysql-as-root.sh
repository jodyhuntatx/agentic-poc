#!/bin/bash

source ./mysql-vars.sh

export POD_NAME=$(kubectl get pods -n $DB_NAMESPACE_NAME --no-headers | awk '{print $1}')

main() {
  kubectl -n $DB_NAMESPACE_NAME exec -it $POD_NAME --	\
        mysql -h $MYSQL_SERVER_ADDRESS -u root --password=$MYSQL_ROOT_PASSWORD 
}

main "$@"
