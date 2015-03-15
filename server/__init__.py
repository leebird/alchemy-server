# use python3 for django and mysql
# replace mysqlidb with pymysql
# http://stackoverflow.com/questions/13320343/can-i-use-mysql-on-djangodev-1-6-x-with-python3-x
import pymysql
pymysql.install_as_MySQLdb()