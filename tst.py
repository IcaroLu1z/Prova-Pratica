import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.animation import FuncAnimation

x = 0
y = 0
# Create axis
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

# Initialize the cube at the initial position
cube = ax.voxels(data, facecolors=colors)

# Function to update the cube's position
def update_position(frame):
    global x, y
    # Update the position of the cube
    x, y = x+10, y+10
    ax.view_init(elev=x, azim=y)


# Create the animation
animation = FuncAnimation(fig=fig, func=update_position, frames=30, interval=30)

plt.show()

def update_cube():
    while True:
        x, y, z = np.random.randint(0,1000, 3)
        x = ((x % 360) + 180) % 360 - 180
        y = ((y % 360) + 180) % 360 - 180
        z = ((z % 360) + 180) % 360 - 180

        ax.view_init(x, y, z)
        plt.draw()
        plt.pause(.06)
    