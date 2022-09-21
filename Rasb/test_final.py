import sys
import os 
import serial
from datetime import datetime
from datetime import date
import pymysql

# Arduino port
port = serial.Serial("/dev/ttyACM0", "57600")

# mysql settings
dbServerIP = '211.214.111.12'
dbUser = 'user'
dbPW = 'ch100300'
db = pymysql.connect(host=dbServerIP, port=3306, user=dbUser, passwd=dbPW, db='Dangsu', charset='utf8')
cursor = db.cursor()

now = datetime.now()
start = date.today()
start_mth = start.month
start_day = start.day
file_title = now.strftime('%Y-%m-%d')

sql = f'''
    CREATE TABLE `${file_title}` (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        time DATETIME NOT NULL,
        data VARCHAR(100) NOT NULL,
        PRIMARY KEY (id)
    );
'''

while True:
    if ((start_day == date.today().day) and (start_mth == date.today().month)):
        file = open('/home/pi/{0}'.format(file_title), 'a')
    else:
        now = datetime.now()
        start = date.today()
        start_day = start.day
        start_mth = start.month
        file_title = now.strftime('%Y-%m-%d')
        file = open('/home/pi/{0}'.format(file_title), 'a')
    while True:
        file1 = open('/home/pi/{0}'.format(file_title), 'a')
        format_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = port.readline().strip()
        file1.write(format_date)
        file1.write(" ")
        file1.write(data)
        file1.write("\n")
        if (start_day != date.today().day or start_mth != date.today().month):
            break
