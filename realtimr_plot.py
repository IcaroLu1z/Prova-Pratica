import serial
import struct
import threading
import numpy as np
import prova
import matplotlib.pyplot as plt

# Configuração da porta serial
PORT = 'COM5'
BAUD_RATE = 9600

# Definição dos protocolos
PACKET_START = [0xAA, 0xFF]
PACKET_END = [0xAF]
PACKET_LENGTH = 8
ID_POSITION = 1
ID_SCALE = 2

# Inicialização dos dados
positions = {'x': [], 'y': [], 'z': []}
scales = []

# Criar uma figura para o matplotlib
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1)

# Curvas de posição
line_x, = ax1.plot([], [], label="X")
line_y, = ax1.plot([], [], label="Y")
line_z, = ax1.plot([], [], label="Z")
ax1.set_title("Position")
ax1.set_xlim(0, 100)
ax1.set_ylim(-180, 180)
ax1.legend()

# Curva de escala
line_scale, = ax2.plot([], [], label="Scale")
ax2.set_title("Scale")
ax2.set_xlim(0, 100)
ax2.set_ylim(0, 2047)
ax2.legend()

def update_plot():
    global positions, scales
    line_x.set_ydata(positions['x'])
    line_x.set_xdata(range(len(positions['x'])))
    
    line_y.set_ydata(positions['y'])
    line_y.set_xdata(range(len(positions['y'])))
    
    line_z.set_ydata(positions['z'])
    line_z.set_xdata(range(len(positions['z'])))

    line_scale.set_ydata(scales)
    line_scale.set_xdata(range(len(scales)))

    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()

    fig.canvas.draw()
    fig.canvas.flush_events()

ser = serial.Serial(PORT, BAUD_RATE)
def serial_listener():
    while True:
        data = prova.unpack_data()
        packet_id, x, y, z = data["packet_id"], data["x"], data["y"], data["z"]

        if int.from_bytes(packet_id, byteorder='big') == ID_POSITION:
            positions['x'].append(x)
            positions['y'].append(y)
            positions['z'].append(z)
            if len(positions['x']) > 100:
                del positions['x'][0]
                del positions['y'][0]
                del positions['z'][0]
        elif int.from_bytes(packet_id, byteorder='big') == ID_SCALE:
            scales.append(x)  # ou y ou z, já que são iguais
            if len(scales) > 100:
                del scales[0]
        update_plot()

def parse_packet(data):
    start, packet_id, x, y, z, checksum, end = struct.unpack('!2B3bBb', data)
    if start != PACKET_START or end != PACKET_END:
        return None, None, None, None
    if (x + y + z + packet_id) & 0xFF != checksum:
        return None, None, None, None
    return packet_id, x, y, z

if __name__ == "__main__":
    thread = threading.Thread(target=serial_listener)
    thread.start()

    plt.show()
