# all the libs used 
import socket
from threading import Thread
import time
import os
import sys

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
            
            msg = conn.recv(2048).decode()

            if msg:

                if msg.startswith('/private'):

                    _, target, privMsg = msg.decode().split(maxsplit=2)

                    if target in clients:

                        c = clients[target]['conn']

                        c.send(f'\n<{nameClient.upper()}>: {privMsg}\n'.encode())

                    else:

                        conn.send('\n[ERRO]>> usuário não encontrado\n'.encode())

                elif msg.startswith('/group'):

                    _, groupName, groupMsg = msg.split(maxsplit=2)

                    if groupName not in grupos:

                        conn.send('\n[ERRO]>> grupo não encontrado\n'.encode())
                        conn.send('\n[CRIAR GRUPO]>> deseja criar grupo com esse nome? se sim, digite "s", se não, "n" \n'.encode())

                        rsp = conn.recv(2048).decode()

                        if rsp == 's':
                            
                            grupos[groupName] = [nameClient]
                            conn.send('\n[MEMBROS]>> digite o nome dos membros a serem adicionados\n'.encode())
                            
                            f = ''
                            
                            while f != '/':
                            
                                f = conn.recv(2048).decode()
                            
                                if f != '/' and f in clients:
                            
                                    grupos[groupName].append(clients[f]['name'])
                            
                            conn.send('grupo feito'.encode())
                            
                            for m in grupos[groupName]:
                                
                                conn.send(m.encode())

                        elif rsp == 'n':

                            conn.send('\n[OK]>>\n')

                    else:

                        j, groupName, groupMsg = msg.split(maxsplit=2)

                        msgEnter = f'\n[{groupName}]>> {nameClient} acabou de entrar\n'

                        broadcastMsg(msgEnter, nameClient, groupName)
                        
                        n = groupMsg

                        broadcastMsg(n, nameClient, groupName)

                        while n != '/leave':

                            nMsg = conn.recv(2048)
                            n = nMsg.decode()

                            if n.startswith('/group'):

                                _, gc, n = n.split(maxsplit=2)
                                
                                if nameClient in grupos[gc]:
                                
                                    broadcastMsg(n, nameClient, gc)
                                
                                else:

                                    conn.send('[ERRO]>> você não está no grupo')
                            
                            elif n.startswith('/private'):

                                _, target, privMsg = n.split(maxsplit=2)

                                if target in clients:

                                    c = clients[target]['conn']

                                    c.send(f'\n<{nameClient.upper()}>: {privMsg}\n'.encode())

                                else:

                                    conn.send('\n[ERRO]>> usuário não encontrado\n'.encode())

                                break

                            elif n.startswith('/file'):

                                _, target, fileName = n.split(maxsplit=2)

                                conn.send(n.encode())
                            
                                with open(fileName, 'rb') as f:

                                    for data in f.readlines():

                                        if target in clients:

                                            targetConn = clients[target]['conn']

                                            targetConn.send(data)
                                            targetConn.send(f'>> arquivo {fileName} enviado'.encode())
                                        
                                        elif target in grupos:

                                            for members in grupos[target]:

                                                memberConn = clients[members]['conn']
                                                    
                                                memberConn.send(data)
                                                memberConn.send(f'[{grupos[target]}]>> arquivo {fileName} enviado'.encode())            
                            
                                break

                            elif n.startswith('/kick'):

                                _, targetName, gc = n.split(maxsplit=2)

                                if nameClient in grupos[gc]:

                                    for h in clients:

                                        if clients[h]['name'] == targetName:

                                            hb = clients[h]['conn']

                                            hb.send(f'\n[REMOVIDO]>> você foi removido pelo admin do grupo {gc}\n'.encode())

                                            for group in grupos:

                                                if h in grupos[group]:

                                                    grupos[group].remove(clients[h]['name'])
                                            
                                                else:

                                                    conn.send('\n[ERRO]>> você não é administrador desse grupo\n'.encode())

                                break

                            elif n.startswith('/quitGroup'):

                                _, groupNome = n.split(maxsplit=1)

                                if groupNome in grupos:

                                    if nameClient in grupos[groupNome]:

                                        grupos[groupNome].remove(nameClient)

                                        conn.send(f'\n[SAIU]>> você saiu do grupo {groupNome}\n'.encode())
                                        broadcastMsg(f'\n[SAIU]>> {nameClient} saiu do grupo {groupNome}\n', nameClient, groupNome)

                                    else:

                                        conn.send('\n[ERRO]>> você não está nesse grupo\n'.encode())

                                else:

                                    conn.send('\n[ERRO]>> esse grupo não existe\n')

                                break

                            else:

                                leaveMsg = f'\n[DESCONECTADO]>> {nameClient} se desconectou do grupo\n'
                                broadcastMsg(leaveMsg, nameClient, groupName)
                                
                                break

                elif msg.startswith('/create'):

                    _, gcName = msg.split()

                    grupos[gcName] = [nameClient]

                    conn.send('\n[MEMBROS]>> digite o nome dos membros a serem adicionados\n'.encode())

                    u = ''

                    while u != '/':

                        u = conn.recv(2048).decode()

                        if u != '/':

                            grupos[gcName].append(clients[u]['name'])
                        
                    conn.send('grupo feito'.encode())
                            
                    for m in grupos[gcName]:
                                
                        conn.send(m.encode())
                
                elif msg.startswith('/file'):

                    _, target, fileName = msg.split(maxsplit=2)

                    conn.send(msg)
                
                    with open(fileName, 'rb') as f:

                        for data in f.readlines():

                            if target in clients:

                                targetConn = clients[target]['conn']

                                targetConn.send(data)
                                targetConn.send(f'>> arquivo {fileName} enviado'.encode())
                            
                            elif target in grupos:

                                for members in grupos[target]:

                                    memberConn = clients[members]['conn']
                                        
                                    memberConn.send(data)
                                    memberConn.send(f'[{grupos[target]}]>> arquivo {fileName} enviado'.encode())

                elif msg.startswith('/kick'):

                    _, targetName, gc = msg.split(maxsplit=2)

                    if nameClient in grupos[gc]:

                        for h in clients:

                            if clients[h]['name'] == targetName:

                                hb = clients[h]['conn']

                                hb.send(f'\n[REMOVIDO]>> você foi removido pelo admin do grupo {gc}\n'.encode())

                                for group in grupos:

                                    if h in grupos[group]:

                                        grupos[group].remove(clients[h]['name'])
                    else:

                        conn.send('\n[ERRO]>> você não é administrador desse grupo\n'.encode())

                elif msg.startswith('/quitGroup'):

                    _, groupNome = msg.split(maxsplit=1)

                    if groupNome in grupos:

                        if nameClient in grupos[groupNome]:

                            grupos[groupNome].remove(nameClient)

                            conn.send(f'\n[SAIU]>> você saiu do grupo {groupNome}\n'.encode())
                            broadcastMsg(f'\n[SAIU]>> {nameClient} saiu do grupo {groupNome}\n', nameClient, groupNome)

                        else:

                            conn.send('\n[ERRO]>> você não está nesse grupo\n'.encode())

                    else:

                        conn.send('\n[ERRO]>> esse grupo não existe\n')

                elif msg == '/quit':

                    print(f'\n[DESCONEXÃO]>> o cliente {nameClient} se desconectou do servidor\n')

                    del clients[nameClient]
                    
                    for group in grupos.keys():
                    
                        if nameClient in group:
                    
                            group.remove(nameClient)
                    
                    print(f'{nameClient} desconectado.')

                    break                    

                elif msg == '/shutdown':

                    serverShutdown()

                elif msg.startswith('/profile'):

                    _, targetNome = msg.split()
                    
                    conn.send(f'\nnome: {clients[targetNome]['name']}'.encode())
                    conn.send(f'\nemail: {clients[targetNome]['email']}'.encode())
                    conn.send(f'\nconn: {str(clients[targetNome]['conn'])}'.encode())
                    conn.send(f'\naddress: {str(clients[targetNome]['addr'])}\n'.encode())

        except Exception as e:

            print(f'\n[ERRO]>> {e}\n')

def serverShutdown():

    print('\n[SHUTDOWN]>> Servidor está desligando...')
    
    for client in clients.keys():
            
            clients[client]['conn'].close()
    
    server.close()
    sys.exit(1)

# function that send messages in groups
def broadcastMsg(msg, sender, groupName):

    if msg.endswith('acabou de entrar\n'):

        if groupName in grupos:

            for member in grupos[groupName]:

                if member != sender:

                    c = clients[member]['conn']

                    c.send(msg.encode())
    
    elif msg.endswith('desconectou do grupo\n'):

        if groupName in grupos:

            for member in grupos[groupName]:

                if member != sender:

                    c = clients[member]['conn']

                    c.send(msg.encode())

    else:
        
        if groupName in grupos:

            for member in grupos[groupName]:

                if member != sender:

                    c = clients[member]['conn']

                    c.send(f'\n<{str(groupName).upper()}><{str(sender)}>: {msg}\n'.encode())

# actually, i didn't even used this function :/
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
