from parameters import *
from base_classes import Node


def get_nodes_position():
    positions = []
    for node in moving_nodes:
        positions.append(node.get_pos())

    return positions
