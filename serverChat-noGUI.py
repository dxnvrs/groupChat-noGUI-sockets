# all the libs used 
import socket
from threading import Thread
import time
import os

#######################################################################################################################################################################################
#                                                                                                                                                                                     #
#                                                          ****************** FUNCTIONS USED *******************                                                                      #
#                                                                                                                                                                                     #
#######################################################################################################################################################################################

# main function, handle the others
def handleClient():

    conn, addr = server.accept()

    emailClient = conn.recv(2048).decode()
    nameClient = conn.recv(2048).decode()

    clients[nameClient] = {'name': nameClient,
                           'email': emailClient, 
                           'conn': conn, 
                           'addr': addr}

    print(f'\n[CONEXÃO BEM SUCEDIDA]>> {nameClient}, de email {emailClient}, se conectou\n')

    while True:

        try:

            msg = str(conn.recv(2048).decode())

            if msg:

                if msg.startswith('/private'):

                    _, target, privMsg = msg.split(maxsplit=2)

                    if target in clients:

                        c = clients[target]['conn']

                        c.send(f'\n<{str(nameClient).upper}>: {privMsg}\n'.encode())

                    else:

                        conn.send('\n[ERRO]>> usuário não encontrado\n'.encode())

                elif msg.startswith('/group'):

                    _, groupName, groupMsg = msg.split(maxsplit=2)

                    if groupName not in grupos:

                        conn.send('\n[ERRO]>> grupo não encontrado\n'.encode())
                        conn.send('\n[CRIAR GRUPO]>> deseja criar grupo com esse nome? se sim, digite "s", se não, "n" \n'.encode())

                        rsp = conn.recv(2048).decode()

                        if rsp == 's':

                            listMembers = []

                            listMembers.append(f'ADM-{nameClient}')

                            conn.send('\n[MEMBROS]>> digite o nome dos membros a serem adicionados\n'.encode())
                            
                            f = ''

                            while f != '/':

                                f = conn.recv(2048).decode()
                                
                                if f != '/':
                                    
                                    listMembers.append(f)

                            grupos[groupName] = listMembers
        
                        elif rsp == 'n':

                            conn.send('\n[OK]>>\n')

                    else:

                        msgEnter = f'\n[{groupName}]>> {nameClient} acabou de entrar\n'

                        broadcastMsg(msgEnter, nameClient, groupName)
                        
                        n = groupMsg

                        while n != '/leave':

                            if n != '/leave':

                                n = conn.recv(2048).decode()
                                broadcastMsg(n, nameClient, groupName)
                            
                            else:

                                leaveMsg = f'\n[DESCONECTADO]>> {nameClient} se desconectou do grupo\n'
                                broadcastMsg(leaveMsg, nameClient, groupName)

                elif msg.startswith('/create'):

                    _, gcName = msg.split(maxsplit=2)

                    listMembers = []

                    listMembers.append(f'ADM-{nameClient}')

                    conn.send('\n[MEMBROS]>> digite o nome dos membros a serem adicionados\n'.encode())

                    u = ''

                    while u != '/':

                        u = conn.recv(2048).decode()

                        if u != '/':

                            listMembers.append(u)
                    
                    grupos[gcName] = listMembers
                
                elif msg.startswith('/file'):

                    _, target, fileName = msg.split(maxsplit=2)
                    fileSize = int(conn.recv(2048).decode())
                    fileData = b''

                    while len(fileData) < fileSize:

                        fileData += conn.recv(2048)

                        with open(fileName, 'wb') as f:

                            f.write(fileData)

                        for i in clients:

                            if clients[i]['conn'] == target:

                                i.send(f'\n[FILE] {fileName}\n'.encode())
                                i.send(str(fileSize).encode())
                                i.send(fileData)

                elif msg.startswith('/kick'):

                    _, targetName, gc = msg.split(maxsplit=2)

                    if f'ADM-{nameClient}' in grupos[gc]:

                        for h in clients:

                            if clients[h]['name'] == targetName:

                                h = clients[h]['conn']

                                h.send(f'\n[REMOVIDO]>> você foi removido pelo admin do grupo {gc}\n'.encode())

                                for group in grupos:

                                    if h in grupos[group]:

                                        listMembers.remove(h)
                                        grupos[group] = listMembers
                    
                    else:

                        conn.send('\n[ERRO]>> você não é administrador desse grupo\n'.encode())

                elif msg.startswith('/quitGroup'):

                    _, groupNome = msg.split(maxsplit=1)

                    if groupNome in grupos:

                        if nameClient in grupos[groupNome] or f'ADM-{nameClient}' in grupos[groupNome]:
                            
                            listMembers.remove(nameClient)
                            grupos[groupNome] = listMembers

                            conn.send(f'\n[SAIU]>> você saiu do grupo {groupNome}\n'.encode())
                            broadcastMsg(f'\n[SAIU]>> {nameClient} saiu do grupo {groupNome}\n', nameClient, groupNome)

                        else:

                            conn.send('\n[ERRO]>> você não está nesse grupo\n'.encode())

                    else:

                        conn.send('\n[ERRO]>> esse grupo não existe\n')

                elif msg.startswith('/quit'):

                    clients[nameClient] = None

                    print(f'\n[DESCONEXÃO]>> o cliente {nameClient} se desconectou do servidor\n')

        except Exception as e:

            print(f'\n[ERRO]>> {e}\n')

# function that send messages in groups
def broadcastMsg(msg, sender, groupName):

    if groupName in grupos:

        for member in grupos[groupName]:

            c = clients[member]['conn']

            c.send(f'\n<{str(groupName).upper()}><{str(sender)}>: {msg}\n'.encode())

# actually, this function i didn't even used :/
def sendMsg(msg, conn, sender):

    try:

        print(f"\n[ENVIANDO]>> enviando mensagens para {conn['addr']}\n")

        msgPraEnviar = str(msg).encode()
        conn['conn'].send(f'\n<{str(sender).upper}>: {msgPraEnviar}\n'.encode())

    except Exception:

        print('\n[ERRO]>> não foi possível enviar essa mensagem\n')

#######################################################################################################################################################################################
#                                                                                                                                                                                     #
#                                                          ****************** CODE STARTS HERE *******************                                                                    #
#                                                                                                                                                                                     #
#######################################################################################################################################################################################

# dicts and lists that contains the registered clients (and their other informations), groups and groups' members  
grupos = {}
clients = {}
listMembers = []

# the host and port choosed (3030 as port 'cause ports of minor values may being used by the computer) ('127.0.0.1' is the localhost's address) 
host = '127.0.0.1'
port = 3030

# instance the server and bind the address to it
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

print('[AGUARDANDO CONEXÃO DE CLIENTE]')

try:

    # server starts to listen to connections
    server.listen()
    print('[TENTATIVA DE CONEXÃO]>> aguardando conexão de um cliente')

except Exception:

    # if it fails, the server closes
    print('[ERRO]>> erro ao tentar conectar um cliente')
    time.sleep(5)
    exit()

# start main loop
while True:

    # threading the main function 'handleClient'
    thread = Thread(target=handleClient)
    thread.start()
