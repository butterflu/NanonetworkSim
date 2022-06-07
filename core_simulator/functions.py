from parameters import *



def get_nodes_position():
    positions = []
    for node in moving_nodes:
        positions.append(node.get_pos())

    return positions


# decorators

def tx_add_stats(phylink):
    stats.transmitted_packets += 1
    stats.transmitted_bits += phylink.bit_size()


def rx_add_stats(phylink):
    stats.received_packets += 1
    stats.received_bits += phylink.bit_size()
