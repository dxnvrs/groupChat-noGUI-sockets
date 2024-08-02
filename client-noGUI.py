# all libs used
import socket
import threading
import time
import os

#######################################################################################################################################################################################
#                                                                                                                                                                                     #
#                                                          ****************** FUNCTIONS USED *******************                                                                      #
#                                                                                                                                                                                     #
#######################################################################################################################################################################################

# main function, handles messages from server  
def recvMsg():

    while True:

        try:

            msg = str(client.recv(2048).decode())

            if msg.startswith('/file'):

                fileName = msg.split(' ', 1)[1]
                fileSize = int(client.recv(2048).decode())
                fileData = b''

                while len(fileData) < fileSize:

                    fileData += client.recv(2048)

                with open(fileName, 'wb') as f:

                    f.write(fileData)

                print(f'\n[FILE]>> arquivo {fileName} recebido\n')

            else:

                print(msg)

        except Exception as e:

            print(f'\n[ERRO]>> não foi possível receber mensagem do servidor. {e}\n')
            break

    return msg

#######################################################################################################################################################################################
#                                                                                                                                                                                     #
#                                                          ****************** CODE STARTS HERE *******************                                                                    #
#                                                                                                                                                                                     #
#######################################################################################################################################################################################

# the host and port choosed (3030 as port 'cause ports of minor values may being used by the computer) ('127.0.0.1' is the localhost's address)
host = '127.0.0.1'
port = 3030

# client is intanced
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:

    # client tries to connect to server
    client.connect((host, port))
    
    # if it makes it, the user have to write their email and name 
    emailUser = input('\n[LOGIN]>> digite seu email:\n')
    print('>> ', emailUser)
    nameUser = input('\n[LOGIN]>> agora, digite seu nome para continuar:\n')
    print('>> ', nameUser)

    # the information is sent to server
    client.send(emailUser.encode())
    client.send(nameUser.encode())

    print('\n[CONECTADO]>> o cliente está conectado\n')

except Exception:
    
    # if it didn't work, client is closed 
    print('\n[ERRO]>> não foi possível conectar o host, pois o servidor está offline.\n')
    time.sleep(5)
    exit()

# start main loop
while True:

    # threading the main function (recvMsg) and starting the process
    process = threading.Thread(target=recvMsg)
    process.start()

    # all messages now are sent to server
    msg = input()
    client.send(msg.encode())
    
    if msg == '/quit':

        print('\n[DESCONECTADO]>> você se desconectou do servidor\n')
        time.sleep(5)
        exit()
