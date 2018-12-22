# Receptor UDP
#
# Aluno: Pedro Campos da Cunha Cavalcanti 
# pcccj@cin.ufpe.br
# Turma: E5
# 2018.2
# 
# Projetado para Funcionamento em ambiente Windows. 

import socket
import _thread as thread
import time

WINDOW_SIZE     = 4     #tam da janela de recbimento (N)
MAX_BUFFER_SIZE = 10    #tam max de pacotes no buffer
MAX_SIZE        = 510   #tam maximo em cada pacote, em dados contido num segmento

STDBY_TIME      = 2.0   #segundos

LOCAL_NAME      = '192.168.25.13' #socket.gethostbyname(socket.gethostname()) 
LOCAL_PORT      = 12000
LOCAL_ADRESS    = (LOCAL_NAME, LOCAL_PORT)
DEST_ADRESS     = ('192.168.25.6', 12000)

rcv_pkts:bytes  = []

def read_pkt(pkt):
    recv_seq_num:int
    ultimoPkt:bool

    header:str      = ( pkt[0:2] ).decode()

    recv_seq_num    = int(header[0])

    if int(header[1]) == 1:
        ultimoPkt = True
    else:
        ultimoPkt = False 

    return (pkt[2:], recv_seq_num, ultimoPkt)

def create_ack(recv_seq_num):
    return str(recv_seq_num).encode()

def send_ack(temp, send_socket, recv_socket): #enviar threads por 3s
    
    # Aguardando por pkts para enviar seus ACKS no tempo de 3s
    while ( ( time.time() - temp ) < STDBY_TIME ):

        try:
            pkt, client_addres = recv_socket.recvfrom(512)
        except:
            return
        
        pkt, recv_seq_num, y = read_pkt(pkt)

        send_socket.sendto( create_ack(recv_seq_num), DEST_ADRESS )
    
def add_to_rcv_pkts(buffer):
    global rcv_pkts

    for pkt in buffer:
        if len(pkt) > 0: # se tiver conteúdo
            rcv_pkts.append(pkt) # add ao arquivo

def join_file(id):
    global rcv_pkts

    file_path = 'Desktop\\' + id.upper() + '.' + id[3:].lower()
    try:
        arquivo = open(file_path, 'wb')
    except:
        print('404! erro ao abrir arquivo!')
        return

    # retira do vetor e escreve no arquivo
    for b in rcv_pkts:
        if len(b) != 0:
            arquivo.write(b)
    
    print('\nArquivo baixado na sua área de trabalho!\n') #del
    arquivo.close()

def join_msg(): 
    global rcv_pkts

    dt:bytes

    # retira do vetor
    for b in rcv_pkts:
        dt = b
    
    return dt.decode()

def receiveFile(send_socket, recv_socket):
    global rcv_pkts

    # Inicializa variaveis da Janela Deslizante
    buffer          :bytes = []
    ult_pkt_rcbido  :int 
    maior_indice_permtdo:int # maior pkt aceitavel
    recv_seq_num    :int
    ultimoPkt       :bool

    # Reseta o array
    rcv_pkts = []

    recv_done:bool = False # Receber quadros até o 'ultimoPkt'

    while not recv_done:

        # inicializa
        buffer = [b''] * MAX_BUFFER_SIZE
        recv_seq_count :int = MAX_BUFFER_SIZE
        window_recv_map:bool = [False] * WINDOW_SIZE

        ult_pkt_rcbido = -1
        maior_indice_permtdo = ult_pkt_rcbido + WINDOW_SIZE

        # Recebe no atual buffer por Janela Deslizante
        while True: 

            # Recebe pacote e traduz
            pkt, client_addess = recv_socket.recvfrom(512)
            pkt, recv_seq_num, ultimoPkt = read_pkt(pkt) 

            # Envia ack:
            send_socket.sendto( create_ack(recv_seq_num), DEST_ADRESS ) 

            if (recv_seq_num <= maior_indice_permtdo):

                buffer_index = recv_seq_num #serve de index p armazenamento

                if (recv_seq_num == ult_pkt_rcbido + 1): #está na sequencia da 'base'

                    buffer[buffer_index] = pkt

                    shift:int = 1

                    for i in range(1, WINDOW_SIZE):
                        if not window_recv_map[i]:
                            break
                        shift += 1
                    
                    for i in range(WINDOW_SIZE - shift):
                        window_recv_map[i] = window_recv_map[i + shift]
                    
                    for i in range(WINDOW_SIZE - shift, WINDOW_SIZE):
                        window_recv_map[i] = False
                    
                    ult_pkt_rcbido += shift
                    maior_indice_permtdo = ult_pkt_rcbido + WINDOW_SIZE

                elif recv_seq_num > ult_pkt_rcbido + 1:# se fora da sequencia da 'base' mas nos limites da janela

                    if not window_recv_map[ recv_seq_num - (ult_pkt_rcbido + 1) ]:
                    
                        buffer[buffer_index] = pkt
                        window_recv_map[recv_seq_num - (ult_pkt_rcbido + 1)] = True
                
                # Definir sequência máxima para sequência de quadros com 'ultimoPkt'
                if ultimoPkt: 
                    recv_seq_count = recv_seq_num + 1 #prazo até acabar...
                    recv_done = True
                
            # Mover para o próximo buffer, se todos os quadros no buffer atual tiverem sido recebidos
            if ult_pkt_rcbido >= recv_seq_count - 1:
                add_to_rcv_pkts( buffer ) #atualiza arquivo
                break

# . . M A I N () . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 


# Criação e inicialização dos sockets
recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.bind(LOCAL_ADRESS)
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Recebe File
receiveFile(send_socket, recv_socket)
    
#Junta tudo no arquivo destino
join_file('004MP3') 

#Iniciar Thread para continuar enviando ACK ao server por 3 segundos
temp = time.time()
thread.start_new_thread( send_ack, (temp, send_socket, recv_socket) )

while ( True ):
    if ( time.time() - temp ) > STDBY_TIME:
        break

print('Done!\n\n') #del
