# Servidor DNS
#
# Aluno: Pedro Campos da Cunha Cavalcanti 
# pcccj@cin.ufpe.br
# Turma: E5
# 2018.2
# 
# Projetado para Funcionamento em ambiente Windows. 

import socket
from random import randint

SERVER_NAME = '192.168.25.10' #<---- ip da maquina
SERVER_PORT = 53 
SERVER_ADRESS = (SERVER_NAME, SERVER_PORT)
SIZE_LIMIT: int = 512 #bytes max para uma transferencia UDP segundo RFC 1035

zonedata = open('Desktop\\projCOM\\database\\zones.txt','r')

def getFlags( flags ):

    byte1:bytes = flags[:1]     # pega o primeiro byte
    byte2:bytes = flags[1:2]    # pega o segundo byte


    QR = '1' #indicando resposta e nao consulta(0)

    OPCODE = '0000'
    #for bit in range(1,5):
    #   OPCODE += str(  ord(byte1) & (1 << bit)  )

    AA = '1' #flag de autoridade: especifica que o servidor de nomes de resposta é uma autoridade
    TC = '0'
    RD = '0'

    # Byte 2

    RA      = '0'
    Z       = '000'
    RCODE   = '0000'


    byte1:bytes = bytes([  int(QR+OPCODE+AA+TC+RD, 2)  ]) #converte em 1 byte ou poderia usar => int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1, byteorder='big')
    byte2:bytes = bytes([  int(RA + Z + RCODE, 2)  ])
   

    return (byte1 + byte2)

def getQuestionDomain(data): #obtem a pergunta/requisicao 

    var_estado  = 0
    tamEsperado = 0
    string      = ''
    dominio_array = []
    tam_str     = 0
    cont        = 0

    for byte in data:

        if var_estado == 1:

            if byte != 0:
                string += chr( byte )

            tam_str += 1

            if tam_str == tamEsperado:
                dominio_array.append(string)
                string = ''
                var_estado = 0
                tam_str = 0

            if byte == 0: # byte == fim
                if string != '': #evita string vazia ser armaznada
                    dominio_array.append(string)
                break

        else: #var_estado = 0
            var_estado = 1
            tamEsperado = byte # obtem o tamanho de uma sequencia N de caracteres do dominio requisitado

        cont += 1 #conta o num de bytes percorridos, a começar do 13º byte 


    tipo_requisicao = data[cont:cont+2] # o primeiro bytes é o \x00 // pega 2 bytes

    return (dominio_array, tipo_requisicao)

def getZone(domain): #verifica o banco de dados de nome de dominios
    global zonedata

    info = ''
    zone_name = '.'.join(domain)

    for line in zonedata.readlines():
        if zone_name in line:
            info += line
            print('   -> Nome de dominio existente')#del

    zonedata.seek(0)

    return info

def getRecords(data): #obtem gravações
    dominio_array, tipo_pergunta = getQuestionDomain(data)
    tp = ''

    if tipo_pergunta == b'\x00\x01': #o qual o primeiro bytes é justo o byte que sinaliza o terino de caracteres na msg
        tp = 'a'
    else:
        print('(!)- - - - TIPO requerido NAO EH "A"!!!') #del

    zone = getZone(dominio_array) #linha da zona requerida

    return (zone, tp, dominio_array)

def buildQuestion( dominio_array, tipo_registro):
    
    qbytes = b''

    for nome in dominio_array:
        length = len(nome)
        qbytes += bytes([length])

        for char in nome:
            qbytes += ord(char).to_bytes(1, byteorder='big')

    if tipo_registro == 'a':
        qbytes += (1).to_bytes(2, byteorder='big')

    qbytes += (1).to_bytes(2, byteorder='big')

    return qbytes

def rectobytes(dominio_array, tipo_pergunta, ttl, value_ip): #records to bytes

    rbytes = b'\xc0\x0c'

    if tipo_pergunta == 'a':
        rbytes += bytes([0]) + bytes([1])

    rbytes += bytes([0]) + bytes([1])

    rbytes += int(ttl).to_bytes(4, byteorder='big')

    if tipo_pergunta == 'a':
        rbytes += bytes([0]) + bytes([4])

        for part in value_ip.split('.'):
            rbytes += bytes([int(part)])

    return rbytes

def buildResponse( data ):

    #Transaction ID
    TransactionID = data[0:2] #primeiro dois bytes
    
    #Obtendo as flags
    Flags = getFlags( data[2:4] ) #pega byte 3,4 (2 bytes)

    # Question Count ou Numero de perguntas
    QDCOUNT = b'\x00\x01'

    # Numero de respostas (RRs)
    ANCOUNT = b'\x00\x01' # 1 pois nesse modelo simples ahvera somente 1 repsosta

    # Nameserver Count
    NSCOUNT = b'\x00\x00'

    # Additonal Count
    ARCOUNT = (0).to_bytes(2, byteorder='big') #b'\x00\x00'

    # cabeçalho montado!
    DnsHeader = TransactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

    # Cria o corpo da resposta DNS
    DnsBody:bytes = b''

    # Obtem resposta para a requisicao/pergunta
    registro, tipo_registro, dominio_array = getRecords(data[12:]) #dados = bytes 13 em diante...
    reg = registro.split()
    try:
        DnsBody = rectobytes( dominio_array, tipo_registro, reg[1] , reg[2] )
    except:
        #print('\n(!) - nome de dominio nao existente no sistema...')
        return b'\x00'

    DnsQuestion = buildQuestion( dominio_array, tipo_registro )

    return DnsHeader + DnsQuestion + DnsBody


#------     MAIN()     -----------------------------------------------------------------------------------------------------------------------


print('# SERVIDOR DNS INICIADO #:')
print('IP: ' + socket.gethostbyname(socket.gethostname()))


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
server_socket.bind( SERVER_ADRESS ) # setando um endereco IP e uma porta no SocketT

while 1:
    data, adress_cliente = server_socket.recvfrom(SIZE_LIMIT)
    print('(*) Pedido realizado pelo cliente:' + str(adress_cliente) )

    r = buildResponse(data)

    #simula perda de dados provavel p/ 20%
    if randint(0,100) < 80:
        server_socket.sendto(r, adress_cliente)
    else:
        print('   -> dado se perdeu...\n')

zonedata.close()
server_socket.close()


