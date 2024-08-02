import socket
import threading
import time
import os

def sendMsg():

    while True:

        mensagem = input()
        
        if mensagem.startswith('/file'):

            _, target, filePath = mensagem.split(' ', 2)
            
            with open(filePath, 'rb') as f:

                fileData = f.read()

            fileName = os.path.basename(filePath)
            client.send(f'/file {target} {fileName}'.encode())
            client.send(str(len(fileData)).encode())
            client.send(mensagem.encode())

        else:

            client.send(mensagem.encode())

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

            elif msg == '/quit':

                print('\n[DESCONECTADO]>> você se desconectou do servidor\n')
                time.sleep(5)
                exit()

            else:

                print(msg)

        except Exception as e:

            print(f'\n[ERRO]>> não foi possível receber mensagem do servidor. {e}\n')
            break

    return msg

host = '127.0.0.1'
port = 3030

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:

    client.connect((host, port))
    
    emailUser = input('\n[LOGIN]>> digite seu email:\n')
    print('>> ', emailUser)
    nameUser = input('\n[LOGIN]>> agora, digite seu nome para continuar:\n')
    print('>> ', nameUser)

    client.send(emailUser.encode())
    client.send(nameUser.encode())

    print('\n[CONECTADO]>> o cliente está conectado\n')

except Exception:

    print('\n[ERRO]>> não foi possível conectar o host, pois o servidor está offline.\n')
    time.sleep(5)
    exit()

while True:

    process = threading.Thread(target=recvMsg)
    process.start()

    msg = input()
    client.send(msg.encode())
