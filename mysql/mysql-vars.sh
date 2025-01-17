export DOCKER=docker
export CLI=kubectl
export DB_NAMESPACE_NAME=mysql
export MYSQL_IMAGE=mysql:8.2.0
export MYSQL_CONTAINER=mysql-xlr8r
export MYSQL_ROOT_PASSWORD=In1t1alR00tPa55w0rd

# MySQL account properties - must exist in PCloud and synced to Conjur
export MYSQL_PLATFORM_NAME=MySQL
export MYSQL_SERVER_ADDRESS=mysql-db.$DB_NAMESPACE_NAME.svc.cluster.local
export MYSQL_SERVER_PORT=3306
export MYSQL_USERNAME=test_user1
export MYSQL_PASSWORD=UHGMLk1
export MYSQL_DBNAME=petclinic
