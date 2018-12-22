# Cliente TCP
#
# Aluno: Pedro Campos da Cunha Cavalcanti 
# pcccj@cin.ufpe.br
# Turma: E5
# 2018.2
# 
# Projetado para Funcionamento em ambiente Windows. 



import time
from random import randint
import socket
import _thread as thread

SERVER_NAME = 'servidor.pcccj.cin'
PORT        = 12000         # 12000 porta escolhida para o programa

MY_NAME     = '192.168.25.9'#               <---- Setar o IP da máquina atual
DNS_SERVER_ADRESS = ('192.168.25.10', 53) # <---- setar IP da maquina DNS

TAM_BYTES_IN: int = 1024

data_recv:bytes = b''       #var global que irá armazenar mensagens DNS, por meio da Thread criada
def gethostbyname(nome_dominio):

    global data_recv

    def readDnsMessage( data ):     #lê os 4 últimos bytes do pacote, captando o ip
        string:str= []

        for byte in data:
            string.append( str(byte) )

        return '.'.join(string)
    
    def waitting(id, dns_socket):   #aguarda recebimento de mensagens vindas do servidor DNS
        global data_recv

        try:
            data_recv, server_dns = dns_socket.recvfrom(512)
        except:
            return None

        return None


    #Cria socket
    dns_socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) #udp
    dns_socket.bind( (MY_NAME, 11000) )

    #Transaction ID (2bytes)
    TransactionID = randint(1,20).to_bytes(2, byteorder='big')

    #Flags (2bytes)
    QR = '0' #consulta
    OPCODE_AA_TC_RD = '0000' + '0' + '0' + '0'
    RA_Z_RCODE = '0' + '000' + '0000'
    Flags = int( QR + OPCODE_AA_TC_RD + RA_Z_RCODE ,2).to_bytes(2, byteorder='big')

    # Question Count ou Numero de perguntas
    QDCOUNT = b'\x00\x01'

    # Numero de respostas (RRs)
    ANCOUNT = b'\x00\x00'

    # Nameserver Count
    NSCOUNT = b'\x00\x00'

    # Additonal Count
    ARCOUNT = b'\x00\x00'

    # cabeçalho montado!
    DnsHeader = TransactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

    # Cria Question
    DnsQuestion = b''
    nome_dominio_array = nome_dominio.split('.')

    for string in nome_dominio_array:
        DnsQuestion += bytes( [ len(string) ] )

        for char in string:
            DnsQuestion += bytes( [ ord(char) ] )

    DnsQuestion += b'\x00' + b'\x00\x01' #marcação de finalização

    #Envia pergunta ao server DNS e aguarda retorno
    thread.start_new_thread(waitting, (1, dns_socket))

    while 1:
        dns_socket.sendto( DnsHeader + DnsQuestion, DNS_SERVER_ADRESS )

        time.sleep(0.5) #aguarda 0.5 segundos, até enviar novamente

        if data_recv != b'\x00' and TransactionID == data_recv[0:2]:
            #lê mensagem recebida pelo server-DNS
            dominio_str = readDnsMessage(data_recv[-4:])
            data_recv = b'' #reseta
            break
        elif data_recv == b'\x00':
            dominio_str = 'Nome de domínio inexistente!'
            data_recv = b'' #reseta
            break
        

    #encerra socket
    dns_socket.close()

    return dominio_str

SERVER_NAME = gethostbyname('servidor.pcccj.cin')
SERVER_ADRESS = (SERVER_NAME, PORT)

def socketConnecting(): #tenta conexão, até conectar...
    aux = True

    while aux:
        try:
            clientSocket.connect(SERVER_ADRESS)
            aux = False
        except:
            print('Tentando conexao com servidor...\n')
            aux = True


def enviaServidor(message):
    # Enviando a mensagem para o Servidor TCP atravÃ©s da conexÃ£o
    try:
        clientSocket.send(message.encode())
    except:
        print("Servidor fora do ar!\nFinalizando aplicação cliente...")
        clientSocket.close()
        quit()


def recebeDoServidor():
    # Retorno da mensg do servidor
    modifiedMessage = clientSocket.recv(1024)
    modifiedMessage = modifiedMessage.decode()

    return modifiedMessage





# ------      MAIN()      ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# criando socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketConnecting()

while True:
    opt = int(input(
        "---------------------------\n(!) Opcoes Disponi­veis:\n---------------------------\n1) Solicitar Arquivo\n2) Listar arquivos disponiveis no servidor\n3) Encerrar conexao\n\nDigite 1, 2 ou 3:"))

    # Se escolheu: Solicitar arquivo
    if opt == 1:
        id = input("Qual o ID do arquivo?\n")
        message = '1' + ' ' + str(id.upper())
        enviaServidor(message)

        file_path = 'Downloads\\' + id + '.' + id[3].lower() + id[4].lower() + id[5].lower()

        # recebendo primeira msg
        dados = clientSocket.recv(50)
        print('bytes=> ' + str(dados.decode()))  # del
        tam = int(str(dados.decode()))  # converte bytes --> str --> int
        tamTotal = tam

        if tam == 404:
            modifiedMessage = "(!) 404 - ID INVALIDA!\n"
        else:
            arquivo = open(file_path, 'wb')  # cria ou edita

            while tam > 0:
                dados = clientSocket.recv(TAM_BYTES_IN)
                tamDados: int = len(dados)
                arquivo.write(dados)
                tam = tam - tamDados
                #percentual enviado
                print('Transferência: ' + str( ((tamTotal - tam)/tamTotal)*100 )[0:4] + "% recebidos..." )  # del

        arquivo.close()
        modifiedMessage = "(!) OK! Arquivo Recebido com sucesso! O arquivo se encontra na pasta \"Downloads\""

    # Se escolheu: Solicitar arquivo
    elif opt == 2:
        message = '2'
        enviaServidor(message)
        # Retorno da mensg do servidor
        modifiedMessage = recebeDoServidor()

    # Se escolheu: Encerrar conexão
    elif opt == 3:
        message = '3'
        enviaServidor(message)
        # Retorno da mensg do servidor
        modifiedMessage = recebeDoServidor()

    print('\nServer return: ' + str(modifiedMessage))

    if message == '3':  # sair
        break

# Fechando o Socket
clientSocket.close()
