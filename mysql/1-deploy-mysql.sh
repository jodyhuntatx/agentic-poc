#!/bin/bash

source ./mysql-vars.sh

main() {
  clean_mysql
  if [[ "$1" == "clean" ]]; then
    exit 0
  fi
  deploy_mysql_db 
  echo "Waiting for MySQL DB to become available..."
  sleep 45
  ./init_mysql.sh
}

########################
clean_mysql() {
  $CLI delete -f ./manifests/mysql-manifest.yaml -n $DB_NAMESPACE_NAME 2> /dev/null
  rm -f ./manifests/mysql-manifest.yaml
}

########################
deploy_mysql_db() {
  $DOCKER pull $MYSQL_IMAGE
  mkdir -p ./manifests
  cat ./templates/mysql-manifest.template.yaml				\
    | sed "s#{{ MYSQL_IMAGE_NAME }}#$MYSQL_IMAGE#g"			\
    | sed "s#{{ CYBERARK_NAMESPACE_NAME }}#$DB_NAMESPACE_NAME#g"  	\
    | sed "s#{{ MYSQL_ROOT_PASSWORD }}#$MYSQL_ROOT_PASSWORD#g"		\
    | sed "s#{{ MYSQL_USERNAME }}#$MYSQL_USERNAME#g"			\
    | sed "s#{{ MYSQL_PASSWORD }}#$MYSQL_PASSWORD#g"			\
    | sed "s#{{ MYSQL_DBNAME }}#$MSQL_DB_NAME#g"			\
    > ./manifests/mysql-manifest.yaml
  $CLI apply -f ./manifests/mysql-manifest.yaml -n $DB_NAMESPACE_NAME
}

main "$@"
