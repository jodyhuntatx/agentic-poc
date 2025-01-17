#!/bin/bash

source ../mysql-vars.sh

export NAMESPACE=mysql
export POD_NAME=mysql-db-0

main() {
  kubectl -n $NAMESPACE exec -it $POD_NAME --	\
        mysql -h $MYSQL_SERVER_ADDRESS -u root --password=$MYSQL_ROOT_PASSWORD 
}

main "$@"
