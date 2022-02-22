from dataclasses import dataclass, field
from math import ceil
import numpy
import random
import simpy
import functions

import binascii
from parameters import *

class Node:
    def __init__(self, env):
        self.antena_gain_db = 10
        self.env = env
        self.channel_resource = simpy.Resource(env, capacity=2)
        self.pos = [0, 0]  # x, y

    def send(self, phylink):
        nodes_in_range = get_nodes_in_range(self, self.get_max_range())
        for node in nodes_in_range:
            # capacity calculation (shanaon's theorem)
            dist = get_dist_between_nodes(self, node)
            print(functions.pathlossforfreq(dist,bandwidht_thz[0]))
            print(functions.pathlossforfreq(dist,bandwidht_thz[1]))
            pathloss = functions.pathlossforfreq(dist, freq_thz)

            capacity = (bandwidht_thz[1]-bandwidht_thz[0])*numpy.log2(1+SNR)
            time = get_transmit_time(phylink, capacity)
            self.env.process(node.start_rcv(phylink))
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
        print("received")


# data classes --------------------------------------------------------------------------------------
@dataclass
class PhyLink:
    payload: bytearray = field(default=numpy.random.bytes(random.randint(10, 100)), metadata={'unit': 'bytes'})

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


def get_dist_between_nodes(node1:  Node, node2: Node):
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5


def get_transmit_time(phylink: PhyLink, capacity):
    return phylink.bit_size() / capacity

#temp function
def queue_send(node, pl):
    while True:
        yield env.timeout(random.randint(1, 3))
        node.env.process(node.send(pl))



# main -----------------------------------
if __name__ == "__main__":
    print("not main")
    all_nodes = []
    pl = PhyLink()
    env = simpy.RealtimeEnvironment()
    n1 = Node(env)
    n2 = Node(env)
    for x in range(3):
        all_nodes.append(Node(env))
    env.process(queue_send(n1,pl))
    print(n1.env)
    env.run()
