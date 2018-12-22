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

LOCAL_NAME      = '192.168.25.6' #socket.gethostbyname(socket.gethostname()) 
LOCAL_PORT      = 12000
LOCAL_ADRESS    = (LOCAL_NAME, LOCAL_PORT)
DEST_ADRESS     = ('192.168.25.13', 12000)

rcv_pkts:bytes  = []
rcv_buffer:bytes= []
recv_done = False

mutex = thread.allocate_lock()

def read_pkt(pkt):
    recv_seq_num:int
    ultimoPkt:bool

    header = ( pkt[0:2] ).decode()

    recv_seq_num    = int(header[0])

    if int(header[1]) == 1:
        ultimoPkt = True
    else:
        ultimoPkt = False 

    return (pkt[2:], recv_seq_num, ultimoPkt)

def create_ack(recv_seq_num):
    return (str(recv_seq_num) + '.........').encode() #10bytes
    
def add_to_rcv_pkts(buffer):
    global rcv_pkts

    for pkt in buffer:
        if len(pkt) > 0: # se tiver conteúdo
            rcv_pkts.append(pkt) # add ao arquivo

def correio(send_socket, recv_socket):
    global mutex
    global rcv_buffer
    global recv_done

    #Ouve qualquer coisa
    while True:
        try:
            data, server_side = recv_socket.recvfrom(512) #Recebe
        except:
            return

        mutex.acquire()

        if not recv_done: #manda as devidas ACKs

            if len(rcv_buffer) <= WINDOW_SIZE:
                rcv_buffer.append(data)

        else: #armazena pkt no rcv_buffer

            pkt, recv_seq_num, y = read_pkt(data)
            send_socket.sendto( create_ack(recv_seq_num), DEST_ADRESS ) 

        mutex.release()

def delivery():
    global rcv_buffer
    package:bytes

    try:
        package = rcv_buffer.pop(0)
    except:
        package = b''

    return package

def join_file(id):
    global rcv_pkts

    #file_path = 'C:/Users/pedro/Desktop/' + id.upper() + '.' + id[3:].lower()
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

    #limpa vetor
    while(1):
        try:
            rcv_pkts.pop()
        except:
            break

    arquivo.close()

def receiveFile(send_socket):
    global rcv_pkts
    global recv_done
    global rcv_buffer

    # Inicializa variaveis da Janela Deslizante
    buffer = []
    ult_pkt_rcbido:int 
    maior_indice_permtdo:int # maior pkt aceitavel
    recv_seq_num:int
    ultimoPkt:bool

    print('Baixando...')

    # Receber pkts até o 'ultimoPkt ' ser identificado
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
            while(True):
                pkt = delivery()
                if len(pkt) > 0:
                    break
            pkt, recv_seq_num, ultimoPkt = read_pkt(pkt) 

            # Envia ack:
            send_socket.sendto( create_ack(recv_seq_num), DEST_ADRESS ) 

            if (recv_seq_num <= maior_indice_permtdo):

                buffer_index = recv_seq_num #serve de index p armazenamento

                if (recv_seq_num == ult_pkt_rcbido + 1): #está na sequencia da 'base'

                    buffer[buffer_index] = pkt

                    shift = 1

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
                    mutex.acquire()
                    recv_done = True
                    rcv_buffer = []
                    mutex.release()
                
            # Mover para o próximo buffer, se todos os quadros no buffer atual tiverem sido recebidos
            if ult_pkt_rcbido >= recv_seq_count - 1:
                add_to_rcv_pkts( buffer ) #atualiza arquivo
                break


# . . M A I N () . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 

# Criação e inicialização dos sockets
recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.bind(LOCAL_ADRESS)
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Arquivos disponíveis
#index = open('Desktop\\projCOM\\database\\index.txt', 'r')
index = open('C:/Users/pedro/Desktop/projCOM/database/index.txt', 'r')

# Inicia Thread para monitorar todo recebimento
thread.start_new_thread(correio, (send_socket, recv_socket))

while True:
    opt = int(input(
        "---------------------------\n(!) Opcoes Disponiveis:\n---------------------------\n1) Solicitar Arquivo\n2) Listar arquivos disponiveis no servidor\n3) Encerrar conexao\n\nDigite 1, 2 ou 3:"))

    # Se escolheu: Solicitar arquivo
    if opt == 1:
        id = input("Qual o ID do arquivo?\n")
        id = id.upper() #caixa alta

        #verifica se o ID existe
        if ( id in index.read() ):
            msg = '1' + ' ' + str(id.upper())

            mutex.acquire()
            recv_done = False
            mutex.release()

            send_socket.sendto(msg.encode(), DEST_ADRESS)

            # Receber arquivo soicitado
            receiveFile(send_socket)

            #Junta tudo no arquivo destino
            join_file(id.upper())

            print('Arquivo Recebido com sucesso! O arquivo se encontra na sua Area de Trabalho \n')
        else:
            print('ID inválido \n')

        index.seek(0)

    elif opt == 2:
        print('Arquivos disponíveis: \n' + index.read() + '\n')
        index.seek(0)
        
    # Se escolheu: Encerrar conexão
    elif opt == 3:
        index.close()
        send_socket.close()
        recv_socket.close()
        exit(1)