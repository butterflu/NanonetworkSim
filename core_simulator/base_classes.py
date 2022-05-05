from dataclasses import dataclass, field
from math import ceil, sqrt
import numpy
import simpy

import binascii
from parameters import *

if use_drihmac:
    from MAC_protocol.DRIH_MAC import *


class Node:
    def __init__(self, env, node_id=1):
        self.antena_gain_db = 10
        self.env = env
        self.channel_resource = simpy.Resource(env, capacity=1)
        self.pos = [0, 0]  # x, y
        self.id = node_id
        self.concurrent_rec_limit = rec_limit
        self.collision_bool = False  # for colission detection
        self.tx_state = False  # for marking if outbound tx is in progress
        self.send_buffer = []
        # energy is expressed as number of bytes able to send rather than any standard energy unit
        self.energy_lvl = 64

        self.env.process(self.recharge())

    def send(self, phylink):
        nodes_in_range = get_nodes_in_range(self, range_mm)
        self.tx_state = True
        time = get_transmit_time(phylink, throuhput_mbps)
        # print(time, "-time")
        time = ceil(time)
        print(self.id, "sent packet at", self.env.now)
        for node in nodes_in_range:
            self.env.process(node.start_rcv(phylink, time))

        yield self.env.timeout(time)
        self.tx_state = False

    def get_pos(self):
        return self.pos

    def start_rcv(self, phylink, transmition_time):
        if len(self.channel_resource.users) > self.concurrent_rec_limit:
            self.collision_bool = True
        else:
            self.collision_bool = False

        with self.channel_resource.request() as req:
            print(self.id, "Start receiving packet at ", self.env.now, "  receiving time:", transmition_time)
            yield self.env.timeout(transmition_time)
            self.recieve_phylink(phylink)

    def recieve_phylink(self, phylink):
        packet_type = phylink.payload[0]

        if self.collision_bool or self.tx_state:
            print(self.id, "colision at ", self.env.now)
        else:
            process_packet(self, phylink, packet_type)

    def recharge(self):
        while True:
            self.energy_lvl = battery_capacity
            yield self.env.timeout(recharge_period)


class AP(Node):
    def __init__(self, env, node_id=1):
        super().__init__(env, node_id)
        self.env.process(self.periodically_send_rtr())

    def send_broadcast_rtr(self):
        print(self.id,"sending broadcast rtr at",self.env.now)
        rtr_packet = RTRPacket()
        rtr_packet.set_parameters(1, 15, self.id, 0, 0, 0, 1, 0, 0, 0, 0, 'broadcast')
        pl = PhyLink(rtr_packet.get_bytearray())
        self.env.process(self.send(pl))

    def periodically_send_rtr(self):
        while True:
            yield self.env.timeout(rtr_interval)
            if not self.tx_state:
                self.send_broadcast_rtr()

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
        return self.byte_size() * 8

    def byte_size(self):
        return len(self.payload)




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


def get_transmit_time(phylink: PhyLink, throughput):
    return phylink.bit_size() / throughput * 1000


# temp function
def periodically_add_data(node: Node, dst_id):
    data_packet=DATAPacket()
    data_packet.set_parameters(0, 10, node.id, dst_id, "data")
    while True:
        yield node.env.timeout(time_gen_function(*time_gen_limits))
        if len(node.send_buffer) >= buffer_size:
            node.send_buffer.pop(0)
        node.send_buffer.append(data_packet)


# main -----------------------------------
if __name__ == "__main__":
    print("not main")

    rtr_packet = RTRPacket()
    rtr_packet.set_parameters(1, 15, 1, 2, 1, 1, 5, 2, 1, 0, 12, 'payload')
    print(rtr_packet)

    data_packet = DATAPacket()
    data_packet.set_parameters(0, 10, 2, 1, "data")
    print(data_packet)

    all_nodes = []
    pl = PhyLink(rtr_packet.get_bytearray())
    print((str(data_packet.get_bytearray())))

    env = simpy.Environment()
    n1 = Node(env, 1)
    n2 = Node(env, 2)
    n2.send_buffer.append(data_packet)

    all_nodes.append(n1)
    all_nodes.append(n2)
    for x in range(3, 5):
        all_nodes.append(Node(env, x))

    # for node in all_nodes:
    #     env.process(queue_send(node, pl))


    print("start sim")
    env.run(30)
