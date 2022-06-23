from parameters import *

def get_nodes_position():
    positions = []
    for node in moving_nodes:
        positions.append(node.get_pos())

    return positions


# temp function



def check_buffer(node):
    if len(node.send_buffer) >= 1:
        return True
    else:
        return False


def get_packet_from_buffer(node):
    if check_buffer(node):
        packet = node.send_buffer[0]
        node.send_buffer.remove(packet)
        return packet
