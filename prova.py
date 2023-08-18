import struct
import csv
import queue
import serial
import threading
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Estrutura do pacote
PACKET_START = [0xAA, 0xFF]
PACKET_END = [0xAF]
PACKET_LENGTH = 8
ID_POSITION = 1
ID_SCALE = 2

data_queue = queue.Queue() # Cria uma fila global data_queue para guardar os dados seriais

def parse_packet(data):
    if len(data) != PACKET_LENGTH:
        return None
    

    # ! - Endianess de rede (big-endian).
    # 2B - start: dois bytes não sinalizados.
    # B - packet_id: um byte não sinalizado.
    # 3b - x, y, e z: três bytes sinalizados.
    # B - checksum: um byte não sinalizado.
    # b - end: um byte sinalizado (se você quiser que seja não sinalizado, substitua por B).

    start1, start2, packet_id, x, y, z, checksum, end = data

    if start1 != PACKET_START or start2 != PACKET_START or end != PACKET_END:
        return None

    # Validar checksum (checksum é a soma dos valores x, y, z e packet_id)
    if (x + y + z + packet_id) & 0xFF != checksum:
        return None

    return packet_id, x, y, z

import struct

def unpack_data():
    state = "START1"  # Initial state
    index = 0  # Index to track current byte position
    result = {}  # Dictionary to store unpacked values

    while 1:
        #byte = data[index]  # Get the current byte
        byte = ser.read(1)

        if state == "START1":
            # Check if the current byte matches the expected value
            if byte == 0xAA:
                state = "START2"  # Move to the next state
            else:
                state = "START1"

        elif state == "START2":
            if byte == 0xFF:
                state = "PACKET_ID"
            else:
                state = "START1"

        elif state == "PACKET_ID":
            result["packet_id"] = byte
            state = "X"

        elif state == "X":
            # Unpack the signed byte using struct and store the value
            result["x"] = struct.unpack('!b', bytes([byte]))[0]
            state = "Y"

        elif state == "Y":
            result["y"] = struct.unpack('!b', bytes([byte]))[0]
            state = "Z"

        elif state == "Z":
            result["z"] = struct.unpack('!b', bytes([byte]))[0]
            state = "CHECKSUM"

        elif state == "CHECKSUM":
            result["checksum"] = byte
            state = "END"

        elif state == "END":
            if byte == 0xAF:
                # All bytes unpacked successfully, return the result
                return result
            else:
                state = "START1"



import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Valores iniciais
SCALE = 1.0

def plot_parallelepiped(x, y, z):
    global SCALE

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Removendo informação do eixo
    ax.axis('off')

    # Criando paralelepípedo sólido
    x_len, y_len, z_len = [SCALE] * 3
    ax.bar3d(0, 0, 0, x_len, y_len, z_len, shade=True)
    
    # Aplicando rotação
    ax.view_init(elev=x, azim=y) 

    plt.show()

def update_scale(scale):
    global SCALE
    SCALE = scale / 2047.0  # Convertendo escala de 0 a 2047 para 0 a 1

import serial
import threading

ser = serial.Serial('COM7', 9600)  # Altere para a porta serial correta

def serial_listener(callback_position, callback_scale):
    while True:
        data = unpack_data()
        packet_id, x, y, z = parse_packet(data)
        if packet_id == ID_POSITION:
            callback_position(x, y, z)
            data_queue.put(("POSITION", x, y, z))
        elif packet_id == ID_SCALE:
            callback_scale(x)
            data_queue.put(("SCALE", x, x, x))  # Note que x=x=y=z nesse caso

def update_position(x, y, z):
    plot_parallelepiped(x, y, z)

def write_to_csv():
    with open('position_data.csv', 'w', newline='') as position_file, \
         open('scale_data.csv', 'w', newline='') as scale_file:

        position_writer = csv.writer(position_file)
        scale_writer = csv.writer(scale_file)

        position_writer.writerow(["Type", "X", "Y", "Z"])
        scale_writer.writerow(["Type", "X"])  # lê apenas um valor, já que x=y=z para este caso

        while True:
            data_type, x, y, z = data_queue.get()

            if data_type == "POSITION":
                position_writer.writerow([data_type, x, y, z])
            elif data_type == "SCALE":
                scale_writer.writerow([data_type, x])


if __name__ == "__main__":
    thread1 = threading.Thread(target=serial_listener, args=(update_position, update_scale))
    thread2 = threading.Thread(target=write_to_csv)
    thread1.start()
    thread2.start()
