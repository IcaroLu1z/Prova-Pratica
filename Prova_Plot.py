import struct
import csv
import queue
import numpy as np
import serial
import threading
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d
from matplotlib.animation import FuncAnimation

# Estrutura do pacote
PACKET_START = [0xAA, 0xFF]
PACKET_END = [0xAF]
PACKET_LENGTH = 8
ID_POSITION = 1
ID_SCALE = 2

SCALE = 1.0

elev, azim = 0, 0

axes = [5, 5, 5]

# Create Data
data = np.ones(axes, dtype=bool)

# Control Transparency
alpha = 1
# Control colour
colors = np.empty(axes + [4], dtype=np.float32)

colors[:] = [1, 0, 0, alpha] # red

# Plot figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.axis('off')

# Voxels is used to customizations of the sizes, positions and colors.
ax.voxels(data, facecolors=colors)

data_queue = queue.Queue() # Cria uma fila global data_queue para guardar os dados seriais

def unpack_data(ser):
    state = "START1"  # Initial state
    result = {}  # Dictionary to store unpacked values

    while True:
        byte = ser.read(1)

        if not byte:
            # No more data to read, break out of the loop
            break

        if state == "START1":
            # Check if the current byte matches the expected value
            if byte == b'\xaa':
                state = "START2"  # Move to the next state
            else:
                state = "START1"

        elif state == "START2":
            if byte == b'\xff':
                state = "PACKET_ID"
            else:
                state = "START1"

        elif state == "PACKET_ID":
            result["packet_id"] = struct.unpack('!b', byte)[0]
            state = "X"

        elif state == "X":
            # Unpack the signed byte using struct and store the value
            result["x"] = struct.unpack('!b', byte)[0]
            state = "Y"

        elif state == "Y":
            result["y"] = struct.unpack('!b', byte)[0]
            state = "Z"

        elif state == "Z":
            result["z"] = struct.unpack('!b', byte)[0]
            state = "CHECKSUM"

        elif state == "CHECKSUM":
            result["checksum"] = struct.unpack('!B', byte)[0]
            if(result["checksum"] == (result["x"] + result["y"] + result["z"] + result["packet_id"])):
                state = "END"
            else:
                state = "START1"

        elif state == "END":
            if byte == b'\xaf':
                # All bytes unpacked successfully, return the result
                return result
            else:
                state = "START1"

def update_scale(scale):
    global SCALE
    SCALE = scale / 2047.0  # Convertendo escala de 0 a 2047 para 0 a 1

ser = serial.Serial('COM8', 9600)  # Altere para a porta serial correta

def serial_listener(callback_position, callback_scale):
    while True:
        data = unpack_data(ser)
        packet_id, x, y, z = data["packet_id"], data["x"], data["y"], data["z"]
       
        if packet_id == ID_POSITION:
            callback_position(x, y, z)
            data_queue.put(("POSITION", x, y, z))
        elif packet_id == ID_SCALE:
            callback_scale(x)
            data_queue.put(("SCALE", x, x, x))  # Note que x=x=y=z nesse caso

def update_position(x, y, z):
    global elev, azim
    elev, azim = x, y

def update_cube(frame):
    #cube = art3d.Poly3DCollection(vertices, alpha=0.8, facecolor='gray')
    #ax.add_collection3d(cube)
    ax.view_init(elev=elev, azim=azim)

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
    ani = FuncAnimation(fig=fig, func=update_cube, frames=60, interval=200)
    plt.show()
