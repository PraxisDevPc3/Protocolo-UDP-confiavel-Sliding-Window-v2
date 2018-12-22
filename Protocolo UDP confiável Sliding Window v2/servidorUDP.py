# Trandmissor UDP
#
# Aluno: Pedro Campos da Cunha Cavalcanti 
# pcccj@cin.ufpe.br
# Turma: E5
# 2018.2
# 
# Projetado para Funcionamento em ambiente Windows.

import socket
import time
import _thread as thread

MAX_BUFFER_SIZE = 10    #tam max de pacotes no buffer
WINDOW_SIZE     = 4     #tam da janela de envio (N)

TIMEOUT         = 1.0   #segundos

window_ack_map:bool     = []
window_sent_time:float  = [] 

ult_ack_receb:int #last ack received
ult_pkt_env:int #last frame sent

mutex = thread.allocate_lock()
msg = ''

#socket infos
LOCAL_NAME      = '192.168.25.13' #socket.gethostbyname(socket.gethostname()) #192.168...
LOCAL_PORT      = 12000
LOCAL_ADRESS    = (LOCAL_NAME, LOCAL_PORT)
DEST_ADRESS     = ('192.168.25.6', 12000)

def create_header(seq_num:int, ult_pkt:bool):
    if ult_pkt:
        return (str(seq_num) + '1').encode()
    else:
        return (str(seq_num) + '0').encode()

def correio(send_socket, recv_socket):
    global ult_ack_receb
    global ult_pkt_env
    global mutex
    global window_ack_map
    global msg

    ack_seq_num:int

    #Ouve qualquer coisa
    while (True):
        try:
            data, client_side = recv_socket.recvfrom(10) #Recebe
            print('', end="")
        except:
            return

        if len(data) == 10:#trata de ACKs
            ack_seq_num = data[0] - 48 #num do pacote recebido pelo receptor

            mutex.acquire()

            if (ack_seq_num > ult_ack_receb) and (ack_seq_num <= ult_pkt_env):
                window_ack_map[ ack_seq_num - (ult_ack_receb + 1) ] = True
                
            mutex.release()
        else:#trata de mensagens

            #mutex.acquire()
            msg = data.decode()
            #mutex.release()

def elapsed_time(time_updated:float, sent_time:float):
    return time_updated - sent_time

def prepareFile(id_do_arquivo:str):
    filePkts = []
    MAX_SIZE = 510

    ext = id_do_arquivo[3:].lower()

    #abre arquivo
    #path = 'C:/Users/pedro/Desktop/projCOM/database/'' + id_do_arquivo + '.' + ext # 001PDF.pdf   002JPG.jpg    003TXT.txt  004MP3.mp3
    path = 'Desktop\\projCOM\\database\\' + id_do_arquivo + '.' + ext # 001PDF.pdf   002JPG.jpg    003TXT.txt  004MP3.mp3
    try:
        arquivo = open(path, 'rb')
    except:
        print('404! erro ao abrir arquivo!') #(!) tem que checar a tabela antes para averiguar se o ID procede, e não por aqui

    data:bytes
    while True:
        data = arquivo.read(MAX_SIZE)

        if(data):
            filePkts.append(data)
        else:
            break        
        
    arquivo.close()

    return filePkts

def fileToBuffer(filePkts):

        num_itens = len(filePkts)
        read_done:bool
        aux:bytes = []

        if num_itens > MAX_BUFFER_SIZE:
            aux = filePkts[:MAX_BUFFER_SIZE]
            del filePkts[0:MAX_BUFFER_SIZE]     #rmve pacotes já transmitidos ao buffer 

            read_done = False 

            return (aux, MAX_BUFFER_SIZE, read_done)

        elif num_itens <= MAX_BUFFER_SIZE:
            aux = filePkts
            del filePkts    #rmve pacotes já transmitidos ao buffer 
            filePkts = []   #zera a lista

            read_done = True
            
            return (aux, num_itens, read_done)

def sendFile(buffer, filePkts, send_socket):
    
    global ult_ack_receb
    global ult_pkt_env
    global mutex
    global window_ack_map
    global window_sent_time
    
    print('Enviando...')
     
    # Atualiza Buffer, Lê Buffer e Envia:
    read_done = False
    while not read_done:

        # Envia parte dos pacotes do 'arquivo' pro Buffer / Seta read_done:
        buffer, buffer_size, read_done = fileToBuffer(filePkts)   
        
        mutex.acquire()

        # Inicializa as variaveis do 'Deslizamento de Janela'
        seq_num:int
        seq_count          = buffer_size 

        window_sent_time   = [0.000] * WINDOW_SIZE
        window_ack_map     = [False] * WINDOW_SIZE
        window_sent_map    = [False] * WINDOW_SIZE
        
        ult_ack_receb = -1
        ult_pkt_env = ult_ack_receb + WINDOW_SIZE #'ult_pkt_env' organiza a chegada de acks...

        mutex.release()

        # Envia buffer atual com Deslizamento de janela ou RepSeletiva 
        send_done = False
        while not send_done: 
            
            mutex.acquire()

            # Checa ''window_ack_map'', e desliza janela se possivel
            if ( window_ack_map[0] ):
                
                shift:int = 1

                #calcula num de aks conscultivos
                for i in range(1, WINDOW_SIZE):
                
                    if not window_ack_map[i]: 
                        break

                    shift += 1
                
                #pegar todas as posiçoes ''a frente'' e colocar no lugar do que já foi contabilizado ex: (v,f,v,v) to (f,v,v,f)
                for i in range(WINDOW_SIZE - shift):
                
                    window_sent_map[i] = window_sent_map[i + shift]
                    window_ack_map[i] = window_ack_map[i + shift]
                    window_sent_time[i] = window_sent_time[i + shift]
                
                #inicializa novas vagas abertas no final com False
                for i in range(WINDOW_SIZE - shift, WINDOW_SIZE):
                
                    window_sent_map[i] = False
                    window_ack_map[i]  = False
                
                ult_ack_receb += shift
                ult_pkt_env = ult_ack_receb + WINDOW_SIZE
            
            mutex.release()


            # Envia pacotes que não foram enviados OU com tempo esgotado
            for i in range(WINDOW_SIZE):
                seq_num = ult_ack_receb + i + 1

                if (seq_num < seq_count): #se True: então ainda existem pacotes a serem enviados, dentro do buffer.

                    mutex.acquire()
                    #nao foi enviado OU tempo esgotado
                    if ( (not window_sent_map[i] ) or ((not window_ack_map[i]) and (elapsed_time(time.time(), window_sent_time[i] ) > TIMEOUT)) ):
                        
                        ultimoPkt:bool = (seq_num == seq_count - 1) and (read_done) #indica o ultimo pacote
                        header = create_header(seq_num, ultimoPkt) 

                        #envia
                        send_socket.sendto(header + buffer[seq_num], DEST_ADRESS) 

                        window_sent_time[i] = time.time()
                        window_sent_map[i] = True
                    
                    mutex.release()
                else:
                    break

            # Vá ao prox Buffer se todos pacotes desse Buffer atual foram confirmados
            if (ult_ack_receb >= seq_count - 1):
                send_done = True

        if (read_done):
            break
    print('Envio realizado com sucesso!')

# . . . M A I N () . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .''' 

print('local host / ip do serv local = ' + LOCAL_NAME + '\n')

# criação dos sockets: send
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp socket
send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# servidor que recebe: recv
recv_socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
recv_socket.bind(LOCAL_ADRESS)

# Carrega arquivo para Enviar:
buffer:bytes = []
buffer_size:int 
header:bytes
filePkts:bytes = [] # 001PDF.pdf   002JPG.jpg    003TXT.txt  004MP3.mp3

# Inicia Thread para monitorar todo recebimento, inclusive d ACKs:
thread.start_new_thread( correio, (send_socket, recv_socket))

choices = ['']
while True:
    #mutex.acquire()
    if len(msg) > 0:
        choices = msg.split()
        msg = ''
        print('[Server say:] Messagem recebida:' + str(choices) )
    #mutex.release()

    #Processa msg recebida:

    if choices[0] == '1':   # Selecionou receber um Arquivo

        #verificar se existe né... (!)
        
        #envia Arquivo
        filePkts = prepareFile(choices[1])
        sendFile(buffer, filePkts, send_socket) 
    
    choices = [''] #reseta
    
    


send_socket.close()
recv_socket.close()
