from dataclasses import dataclass, field
from math import ceil
import numpy
import random
import simpy
import functions

import binascii
from parameters import *

if use_drihmac:
    from MAC_protocol.DRIH_MAC import RTRPacket


class Node:
    def __init__(self, env, node_id=1):
        self.antena_gain_db = 10
        self.env = env
        self.channel_resource = simpy.Resource(env, capacity=2)
        self.pos = [0, 0]  # x, y
        self.id = node_id

    def send(self, phylink):
        nodes_in_range = get_nodes_in_range(self, self.get_max_range())
        for node in nodes_in_range:
            # capacity calculation (shanaon's theorem)
            # dist = get_dist_between_nodes(self, node)
            # print(functions.pathlossforfreq(dist, bandwidht_thz[0]))
            # print(functions.pathlossforfreq(dist, bandwidht_thz[1]))
            # pathloss = functions.pathlossforfreq(dist, freq_thz)

            # capacity = (bandwidht_thz[1] - bandwidht_thz[0]) * numpy.log2(1 + SNR)
            # time = get_transmit_time(phylink, capacity)
            self.env.process(node.start_rcv(phylink, 2))
        yield self.env.timeout(5)

    def get_pos(self):
        return self.pos

    def get_max_range(self):
        return 20

    def start_rcv(self, phylink, transmition_time):
        with self.channel_resource.request() as req:
            yield req
            print(self.channel_resource.users, "at ", self.env.now, "for node:", all_nodes.index(self))
            yield self.env.timeout(3)
            self.recieve_phylink(phylink)

    def recieve_phylink(self, phylink):
        # temporary
        rtr_packet = RTRPacket(phylink.payload)
        print("received packet:", rtr_packet)

    # DRIH-mac
    def send_RTR(self, dst_id=2):
        seq = 1
        rtr_packet = RTRPacket()
        rtr_packet.set_parameters(seq, self.id, dst_id, 0, 0, 1, 0, 0, 0, 0, "payload")
        self.env.process(self.send(PhyLink(rtr_packet.get_bytearray())))


# data classes --------------------------------------------------------------------------------------
@dataclass
class PhyLink:
    def __init__(self, payload=None):
        if not payload:
            self.payload: bytearray = field(default=numpy.random.bytes(random.randint(10, 100)),
                                            metadata={'unit': 'bytes'})
        else:
            self.payload = payload

    def __str__(self):
        binary = str(binascii.hexlify(bytearray(self.payload)))
        return binary

    def bit_size(self):
        return len(str(self))

    def byte_size(self):
        return ceil(self.bit_size() / 8)


class BusyChannel(Exception):
    """Exception for handling channel collisions"""

    def __init__(self):
        self.message = "packets collided"


# functions ----------------------------------------------------------------
def get_nodes_in_range(node: Node, max_range: float):
    nodes_in_range = []
    for n2 in [n for n in all_nodes if n is not node]:
        distance = get_dist_between_nodes(node, n2)
        if distance <= max_range:
            nodes_in_range.append(n2)
        else:
            print("no range")
    # print(nodes_in_range)
    return nodes_in_range


def get_dist_between_nodes(node1: Node, node2: Node):
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5


def get_transmit_time(phylink: PhyLink, capacity):
    return phylink.bit_size() / capacity


# temp function
def queue_send(node, pl):
    while True:
        yield env.timeout(random.randint(1, 3))
        node.env.process(node.send(pl))


# main -----------------------------------
if __name__ == "__main__":
    print("not main")

    rtr_packet = RTRPacket()
    rtr_packet.set_parameters(15, 1, 1, 1, 1, 5, 2, 1, 0, 12, '2345678345678')
    print(rtr_packet)

    all_nodes = []
    pl = PhyLink(rtr_packet.get_bytearray())
    env = simpy.Environment()
    n1 = Node(env)
    n2 = Node(env)
    for x in range(3):
        all_nodes.append(Node(env, x))

    for node in all_nodes:
        node.send_RTR()
    env.run()
