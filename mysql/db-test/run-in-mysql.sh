#!/bin/bash

source ../mysql-vars.sh

export NAMESPACE=$DB_NAMESPACE_NAME
export POD_NAME=mysql-db-0
export DB_URL=$MYSQL_SERVER_ADDRESS
export DB_NAME=$MYSQL_DBNAME

main() {
  if [[ $# != 2 ]]; then
    echo "Usage: $0 <sql-command-filename> <num-iterations>"
    exit -1
  fi
  export SQL_CMD_FILE=$1
  export NUM_ITERATIONS=$2
set -x
  echo

  for i in $(seq 1 $NUM_ITERATIONS); do
    cat $SQL_CMD_FILE					\
    | kubectl -n $NAMESPACE exec -i $POD_NAME --	\
        mysql -h $DB_URL -u $MYSQL_USERNAME --password=$MYSQL_PASSWORD $DB_NAME
  done
}

main "$@"
