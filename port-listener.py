from io import StringIO
import csv
import socket
import codecs
import subprocess as sbp
from subprocess import CREATE_NEW_CONSOLE


#sbp.call(['/home/gnuradio/dump1090_sdrplus-master/dump1090', '--interactive' , '--net' , '--net-ro-port' , '30002' , '--net-sbs-port' , '30003'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
sbp.Popen('cmd', creationflags=CREATE_NEW_CONSOLE)
input('Enter to exit from Python script...')

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('yeep')
ip=socket.gethostbyname("0.0.0.0")
port=30003
address=(ip,port)
client.connect(address)  ## <--Add this line.

count = 0
while True:
    print("########################################")

    data = client.recv(1024)

    decoded_data = codecs.decode(data).strip()

    parsed_data = list(map(str.strip, decoded_data.split()))

    print(parsed_data)


    ## hex = parsed_data[4]
    ## flight# = parsed_data[10]
    ## altitude = ...[11]
    ## speed = ...[12]
    ## track = ...[13]
    ## latitude = ...[14]
    ## longitude = ...[15]
    ## 


# 