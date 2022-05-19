from base_classes import Node
from numpy.random import beta, uniform
from parameters import *
import numpy as np

import matplotlib.pyplot as plt

"""
For 1 node setup, ap-node is in 0;0     for multi ap-node setup, y is set in 0

-------negative x values--------ap-node(0;0)-----------positive x values-----------y=0
        o           o       o           o           o           o
            o           o                   o           o
  o         o   o       o           o           o           o       o
-----------------------------------------------------------------------------------y=vein diameter

simulator works in 2D but to accommodate for loss in 3rd dimension, nodes can 'stack' on top of each other
 and they are more likely to be in the middle (beta distribution) but x value is uniform (and static)
 
All x,y values are in mm
"""
num_simulated_nodes = int(sim_time_s * velocity_mmps / 100 * np.pi * ((vein_diameter_mm/100) ** 2) / blood_volume_l * nodes_num)
print(num_simulated_nodes)
size = num_simulated_nodes
x_start = -np.ceil((sim_time_s * velocity_mmps) + 10)
x_end = -10

y_beta = beta(2, 2, size=size) * vein_diameter_mm
y_values = [round(x, 2) for x in y_beta]

x_uniform = uniform(x_start, x_end, size=size)
x_values = [round(x, 3) for x in x_uniform]

con = np.stack((x_values, y_values), axis=1)
# print(con)

fig, ax = plt.subplots()
ax.scatter(x_values, y_values)
plt.show()


# TODO: add nodes to all nodes and mobility nodes
# move all nodes to the right
def move_nodes():
    for node in moving_nodes:
        node.pos[0] = node.pos[0] + velocity_mmps * step
