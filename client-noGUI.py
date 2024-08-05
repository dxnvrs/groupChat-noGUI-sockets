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
            
            msg = client.recv(10000).decode()

            if msg.startswith('/file'):

                _, target, file_path = msg.split(maxsplit=2)
            
                with open(file_path, 'wb') as f:

                    while True:

                        data = client.recv(10000)
                        
                        if not data:
                            break
                        
                        f.write(data)

            else:

                print(msg)

        except Exception as e:

            print(f'\n[ERRO]>> não foi possível receber mensagem do servidor. {e}\n')
            break

# send messages function 
def sendMsg():
    
    while True:
        
        message = input()
        
        if message.startswith("/file"):

            client.send(message.encode())

        elif message == '/quit':

            client.send(message.encode())

            print('\n[DESCONECTADO]>> você se desconectou do servidor\n')
            time.sleep(5)
            client.close()
            
            break

        elif message == '/shutdown':

            print('[OFF]>> servidor está desligando...')
            client.send(message.encode())

        elif message.startswith('/private') or message.startswith('/group'):
        
            client.send(message.encode())
            _, target, msgRecebida = message.split(maxsplit=2)
            print(f'\n<YOU>: {msgRecebida}\n')

        else:

            client.send(message.encode())

def main():

    # the host and port choosed (3030 as port 'cause ports of minor values may being used by the computer) ('127.0.0.1' is the localhost's address)
    host = '127.0.0.1'
    port = 3030

    global client

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

    # threading the main function (recvMsg) and starting the process
    process = threading.Thread(target=recvMsg)
    process.start()

    # all messages now are sent to server
    sendMsg()

#######################################################################################################################################################################################
#                                                                                                                                                                                     #
#                                                          ****************** CODE STARTS HERE *******************                                                                    #
#                                                                                                                                                                                     #
#######################################################################################################################################################################################

if __name__ == '__main__':

    main()
