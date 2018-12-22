# Servidor TCP
#
# Aluno: Pedro Campos da Cunha Cavalcanti 
# pcccj@cin.ufpe.br
# Turma: E5
# 2018.2
# 
# Projetado para Funcionamento em ambiente Windows. 


import socket

MY_NAME = '192.168.25.9' #<--- Ip da mquina
MY_PORT = 12000
MY_ADRESS = (MY_NAME, MY_PORT)

def listarArquivos(): # abre documento de texto index.txt e retorna
    contador = 0
    texto = ''
    arquivo = open('Desktop\\projCOM\\database\\index.txt','r')

    texto = arquivo.read()
    arquivo.seek(0)#zera ponteiro.

    #contar num de linhas/arquivos
    for linha in arquivo:
        contador += 1

    arquivo.seek(0)
    arquivo.close()

    return 'Existem 0' + str(contador) + ' Arquivos disponíveis:\n' + texto

def sendArquivo(id):  

    id = id.upper()
    path = 'Desktop\\projCOM\\database\\'
    nome = id + '.' + id[3].lower() + id[4].lower() + id[5].lower()
    path = path + nome
    tam = 0

    try:
        arquivo = open(path, 'rb')
    except:
        #envia Mensagem de erro
        print('404! Arquivo selecionado nao existe!')
        conectionSocket.send( str(404).encode() )
        return
    
    fyle = arquivo.read()
    
    #prim mensagem
    tam  = len( fyle )
    conectionSocket.send( str(tam).encode() )
    
    #envia Mensagem/arquivo
    conectionSocket.send( fyle ) #j[a est[a em bytes]]

    print('Arquivo totalmente enviado!')

    arquivo.seek(0)
    arquivo.close()

def verifSeguranca( m ): #tratando o erro do Cliente quebrar e enviar uma mensagem vazia tipo '', dai vai quebrar nos 'if(s)' que verificam vetor na primeira posicao
    try:
        if m[0] == 'a':#se isso der erro vai retonar algo valido no except:
            pass
    except:
        return 'bla'
    
    return m


#------ main() ---------------------------------------------------------------------------------------------------------#

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
#setando um endereco IP e uma porta no Socket
serverSocket.bind(MY_ADRESS)
#setando socket em modo passivo
serverSocket.listen(1)

print('\nServidor TCP iniciado no IP:' + MY_NAME + ' e porta:' + str(MY_PORT) + '\n')

while True:
    #sempre em busca de aceitar uma nova conexao...
    conectionSocket, cliente = serverSocket.accept()
    print('Conexao realizada por:' + str(cliente) )
    
    while True:
        #recebe mensagem
        try:
            message = conectionSocket.recv(1024)
            message = verifSeguranca(message)
        except:
            print('Cliente: ' + str(cliente) + ' desconectou inesperadamente! \n')
            break
        message = message.decode()
        print('Messagem recebida:' + str(message) )

        #Processa msg recebida:
        
        if message[0] == '1':   #Selecionou receber um Arquivo
            message = message.split()
            message = message[1]#ID do arquivo requerido
            
            sendArquivo(message)


        elif message[0] == '2': #Selecionou Listar Arquivos Disponiveis
            print('\nListando arquivos disponíveis para transferência...')
            message = listarArquivos()

            #envia Mensagem
            conectionSocket.send( message.encode() )

        elif message[0] == '3': #Selecionou Sair
            message = 'Servidor está encerrando essa conexão...' 

            #envia Mensagem
            conectionSocket.send( message.encode() )

            print('\nEncerrando conection...')
            break
        

    #Encerrando conexão
    conectionSocket.close()


    '''
def waitingACK(ack_esperado, recv_socket):
    global confirmation

    while True:
        try:
            data, client_side = recv_socket.recvfrom(512)
        except:
            return None

        m_ack = data.decode()

        if m_ack == ack_esperado: 
            mutex.acquire()
            confirmation = True
            mutex.release()
            break

    return None

def enviaServidor(message, send_sock, recv_socket, ack_esperado):
    global confirmation

    #espera ACK
    thread.start_new_thread( waitingACK, (ack_esperado, recv_socket) )
    
    #envia até receber confirmação de ACK
    while True:
        send_sock.sendto(message.encode(), DEST_ADRESS)

        time.sleep(0.008) #aguarda 0.008 segundos, até enviar novamente

        if confirmation:
            confirmation = False #reseta
            break
    '''