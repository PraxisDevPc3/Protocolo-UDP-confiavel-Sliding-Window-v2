import socket
import threading
import time
import random
from math import ceil

#Transmissor/Servidor

MAX_DATA_SIZE   = 500   #tam maximo em cada pacote, em dados
MAX_BUFFER_SIZE = 10    #tam max de pacotes no buffer
WINDOW_SIZE     = 4     #tam da janela de envio (N)

TIME_OUT        = 1.5   #tempo de espera por reconhecimento

PERCENT_LOSE_PKT= 50    #chance de perda de pacote

snd_pkts:bytes  = []     #buffer de pacotes a serem enviados
base            = 0      #indice base da janela (pacotes recnhecidos)
lastPkt         = 0      #indice do ultimo pacote no buffer

start_timer = 0         #temporizador

#semáforos para controle de regioes criticas
lock        = threading.Semaphore()    #para base da janela
time_lock   = threading.Semaphore()    #para o marcador de tempo/temporizador

#socket info
LOCAL_NAME      = socket.gethostbyname(socket.gethostname()) #192.168...
LOCAL_PORT      = 12000
LOCAL_ADRESS    = (LOCAL_NAME, LOCAL_PORT)
DEST_ADRESS     = ('192.168.25.13', 12001)

'''
def makePackage(string):
    global lastPkt
    global pkts
    str_size = len(string)

    if str_size <= MAX_DATA_SIZE * MAX_BUFFER_SIZE:
        lastPkt = (str_size - 1) // MAX_DATA_SIZE #indice do ultimo fragmento da msg
        i = 0

        while i < str_size:
            data = string[i:i + MAX_DATA_SIZE]  # guarda parte da mensagem no pacote

            # determina o bit de fragmentação do pacote
            if i // MAX_DATA_SIZE == lastPkt:
                frag = '1'
            else:
                frag = '0'

            pkt = str(len(pkts)) + frag + data  # adiciona o cabeçalho
            pkts.append(pkt)

            i += MAX_DATA_SIZE
    else:
        print('Mensagem muito grande para ser enviada!')

'''

def strToBytes( string ):
    #apos transformar bytes em str(bytes), voce pode realizar a desconversao aqui
    by:bytes = string[2:-1].encode('latin1').decode('unicode_escape').encode('latin1')

    return by

# Main() . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 

print('local host / ip do serv local = ' + LOCAL_NAME )

# criação dos sockets: send
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp socket
send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# servidor que recebe: recv
recv_socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
recv_socket.bind(LOCAL_ADRESS)

path = 'Desktop\\projCOM\\database\\004MP3.mp3' # 001PDF.pdf   002JPG.jpg    003TXT.txt  004MP3.mp3
try:
    arquivo = open(path, 'rb') #pode dar merda se nÃ£o existir
except:
    print('404! erro ao abrir arquivo!')

tam_arquivo = len( arquivo.read() )
arquivo.seek(0)
num_de_pkts = ceil( (tam_arquivo)/(MAX_DATA_SIZE) )

data:bytes
pkt_index = 0
aux = ''
size:int
sinalizador = '' # sinaliza quando o tamanho do segmento é menor, ou seja o ultimo
while True:
    data = arquivo.read(MAX_DATA_SIZE)
    if(data):
        size = len(data)

        if( size == MAX_DATA_SIZE):
            sinalizador = '0' # size = 500
            
            if(pkt_index == 0):
                data = (sinalizador + str(pkt_index) + " " + str(num_de_pkts)).encode() + data # cabecalho = sinalizador+pkt_index ' ' num_de_pkts
            else:
                data = (sinalizador + str(pkt_index) + " " + str(size)).encode() + data # cabecalho = sinalizador+pkt_index ' ' tamanho de dados do segmento
        else:
            sinalizador = '1' # size < 500

            #-----calculo do tam_de_cabc
            aux2 =  (sinalizador + '00' + str(pkt_index) + " " + str(size)).encode() #designa dois bytes = indica tam_do_cabc
            
            if len(aux2) < 10: # se tem menos de duas casas
                aux = '0' + str( len(aux2) )
            else:
                aux = str( len(aux2) )

            print('TAM do cabc:') #del
            print(aux) #del
            #-----fim calculo tam_do_cbc

            data = (sinalizador + aux   + str(pkt_index) + " " + str(size)).encode() + data # cabecalho = sinalizador+pkt_index ' ' tamanho de dados do segmento
           

        snd_pkts.append(data)
        pkt_index += 1
        
    else:
        break        
    
if (pkt_index ) != num_de_pkts: #del
    print('ERRO! ******* pkt_index ' + str(pkt_index +1) + '!= num_de_pkts_ '+ str(num_de_pkts) )

arquivo.close()

print('numero de itens no vetor snd_pkts=' + str(len(snd_pkts))) #del

for pkt in snd_pkts:
    send_socket.sendto(pkt, DEST_ADRESS)
    time.sleep(0.0005) #delay de 0.1segundo

''' while(True): #apagar
        send_socket.sendto(pkt, CLIENT_ADRESS)
        time.sleep(3) #delay de 1segundo
'''
    


















'''
#loop de mensagens:
while True:
    pkts = []
    base = 0

    #makePackage(string) #quebrar a mensagem em pacotes menores

    if len(pkts) > 0: #Um controle de janela é chamado, caso o tamanho da mensagem seja maior que zero.
        controlWindow_N()
    
'''
send_socket.close()
recv_socket.close()



'''
teste3 = '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\xff\xdb\x00C\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\xff\xc0\x00\x11\x08\x04\x1a\x06\x90\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x01\x00\x01\x05\x00\x03\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x05\x06\x07\t\n'
teste3 = teste3.encode('latin1').decode('unicode_escape').encode('latin1')


teste22 = teste2[2:-1].encode('latin1').decode('unicode_escape').encode('latin1')
'''