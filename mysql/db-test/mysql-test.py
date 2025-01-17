#!/usr/bin/python3

import mysql.connector
from mysql.connector import errorcode

config = {
  'user': 'test_user1',
  'password': 'UHGMLk1',
  'host': '192.168.49.2',       # minikube ip
  'port': '32509',              # nodeport
  'database': 'petclinic',
  'raise_on_warnings': True
}

try:
  cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

cursor = cnx.cursor()

query = ("select name, birth_date from pets")

cursor.execute(query)

for (name, birth_date) in cursor:
  print("{} was born on {:%d %b %Y}".format(
    name, birth_date))

cursor.close()
cnx.close()
