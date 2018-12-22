import socket

MAX_DATA_SIZE   = 500   #tam maximo em cada pacote, em dados contido num segmento

# dados do host local(recv) e destino(send)
LOCAL_NAME      = socket.gethostbyname(socket.gethostname()) #192.168...
LOCAL_PORT      = 12001
LOCAL_ADRESS    = (LOCAL_NAME, LOCAL_PORT)
DEST_ADRESS     = ('', 12000)

def strToBytes( string ):

    #string = "b'" + string + "'"

    #apos transformar bytes em str(bytes), voce pode realizar a desconversao aqui
    by:bytes = (string).encode('latin1').decode('unicode_escape').encode('latin1')

    return by

def criaVetor( tam ):
    v = []
    for i in range(tam):
        v.append(b'')
    
    return v

def readHeader( data, sinalizador ):

    string = data.decode()

    pkt_index = ''
    size_data = ''
    num_total_pkts = ''
    v:int = 0

    if sinalizador == 0:
        for c in string:

            if c == ' ':
                v += 1

            elif v == 0:
                pkt_index += c
            elif v == 1:
                if int(pkt_index) == 0:
                    num_total_pkts += c
                else:
                    size_data += c
            else:
                break

        if int(pkt_index) == 0:
            return ( int(pkt_index), int(num_total_pkts), None ) #tupla
        else:
            return ( int(pkt_index), int(size_data), None ) #tupla

    else: #sinalizador == 1
        for c in string:

            if c == ' ':
                v += 1

            elif v == 0:
                pkt_index += c
            elif v == 1:
                if int(pkt_index) == 0:
                    size_data += c
                    num_total_pkts = '1' #deduz-se
                else:
                    size_data += c
            else:
                break
            
        if num_total_pkts == '1':
            return ( int(pkt_index), int(size_data), int(num_total_pkts) ) #tupla
        else:
            return ( int(pkt_index), int(size_data), None ) #tupla
    

#
print('IP do Host Local =' + LOCAL_NAME)

# criação e inicialização dos sockets
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(LOCAL_ADRESS)

send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# arquivo
path = 'Desktop\\004MP3.mp3' #001PDF.pdf   002JPG.jpg   003TXT.txt   004MP3.mp3
try:
    arquivo = open(path, 'wb') #pode dar merda se nÃ£o existir
except:
    #envia Mensagem de erro
    print('404! erro ao abrir arquivo!')

num_pkts    = None
v           = []
n:int
data:bytes
tam_do_cabc:int
cabecalho:tuple
pkts_recebidos = 0
# loop receptor de mensagens
while True:
    # recebe e decodifica a mensagem:

    (pkt, addr) = recv_sock.recvfrom(520) #520 no pior caso, mas mantendo uma média <= á 512bytes
    n = int(pkt[0]) - 48 # 0 = 48 e #1 = 49

    print('tam do pckt(' + str(pkts_recebidos + 1) + ') = ' + str(len(pkt)) + 'bytes') #del

    if n == 0: # sinalizador = 0, segmento normal
        tam_do_cabc = len(pkt) - MAX_DATA_SIZE
        data = pkt[tam_do_cabc:]
        cabecalho = readHeader( pkt[1:tam_do_cabc], n) # (0):pkt_index (1)num_de_pkts/size_data
        n = cabecalho[0]

        if n == 0:
            v = criaVetor(cabecalho[1])
            num_pkts = int(cabecalho[1])

        try:
            v[n] = data
            pkts_recebidos += 1
        except:
            print('Error: Ainda não recebeu PKT 0')
        
        if pkts_recebidos == num_pkts:
            break

    else: # segmento anormal n==1

        # capta tam_do_cabc byte[2 até o 3] XX
        tam_do_cabc = ( ( int(pkt[1]) -48 )*10 ) + ( int(pkt[2]) - 48 ) 

        cabecalho = readHeader( pkt[3:tam_do_cabc], n ) # (0):pkt_index (1)size_data (2)num_de_pkts

        n = cabecalho[0]
        data = pkt[tam_do_cabc:]
        
        if n == 0:
            v = criaVetor(cabecalho[2]) # ou seja criaVetor(1)
            num_pkts = int(1)
        
        try:
            v[n] = data
            pkts_recebidos += 1
        except:
            print('Error: indice não encontrado no vetor de pacotes recebidos')
        
        if pkts_recebidos == num_pkts:
            break

    print(str(pkts_recebidos) + ' pacotes de um total de ' + str(num_pkts) + ' ')#del

# retira do vetir/buffer de recebimento e escreve no arquivo
for by in v:
    if by == b'':
        print('PKT PERDIDO')

    arquivo.write(by)

print('fim') #del
arquivo.close()

recv_sock.close()
send_sock.close()
