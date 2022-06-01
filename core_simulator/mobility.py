from base_classes import Node, AP, periodically_add_data
from numpy.random import beta, uniform
from parameters import *
import numpy as np
from simpy import Environment

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

#calucating several parameters to limit the simulation scope
num_simulated_nodes = int(
    sim_time_s * velocity_mmps / 100 * np.pi * ((vein_diameter_mm / 100) ** 2) / blood_volume_l * nodes_num)
size = num_simulated_nodes
x_start = -np.ceil((sim_time_s * velocity_mmps) + 10)
x_end = -10


# move all nodes to the right
def move_nodes():
    for node in moving_nodes:
        node.pos[0] = node.pos[0] + velocity_mmps * step


def start_mobility(env: Environment):
    while True:
        yield env.timeout(1)
        # print("tick", env.now)
        move_nodes()


def setup_nodes(env):
    """
    function to set up nodes and assign them to propper lists
    :return:
    """
    #randomize positions, beta 1,1 - uniform, beta 2,2 - dome shaped distribution
    y_beta = beta(1, 1, size=size) * vein_diameter_mm
    y_values = [round(x, 2) for x in y_beta]

    x_uniform = uniform(x_start, x_end, size=size)
    x_values = [round(x, 3) for x in x_uniform]

    pos_combined = np.stack((x_values, y_values), axis=1)


    # add nano-router
    all_nodes.append(AP(env=env, node_id=1))

    for node_id, pos in zip(range(2, num_simulated_nodes + 1),pos_combined):
        node = Node(env=env, node_id=2)
        node.pos = pos
        # env.process(periodically_add_data(node, 1))
        all_nodes.append(node)
        moving_nodes.append(node)

    env.process(start_mobility(env))
    print("Added", num_simulated_nodes, "nodes")




if __name__ == "__main__":
    print(num_simulated_nodes)
    y_beta = beta(2, 2, size=size) * vein_diameter_mm
    y_values = [round(x, 2) for x in y_beta]

    x_uniform = uniform(x_start, x_end, size=size)
    x_values = [round(x, 3) for x in x_uniform]

    con = np.stack((x_values, y_values), axis=1)
    print(con)

    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values)
    plt.show()
