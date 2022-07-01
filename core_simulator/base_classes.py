import random
from dataclasses import dataclass, field
from math import ceil, sqrt

import numpy
import simpy
import logging

import binascii
import parameters as param


class Node:
    def __init__(self, env, node_id=1, position=(0, 0, 0)):
        self.position = position
        self.env = env
        self.channel_resource = simpy.Resource(env, capacity=1)
        self.pos = [0, 0, 0]  # x, y, z
        self.id = node_id
        self.concurrent_rec_limit = param.rec_limit
        self.collision_bool = False  # for colission detection
        self.tx_state = False  # for marking if outbound tx is in progress
        self.rx_on = False  # to mark when receiving is on
        self.send_buffer = []
        # energy is expressed as number of bytes able to send rather than any standard energy unit
        self.energy_lvl = 64

        self.env.process(self.recharge())

        self.surrounding_node_list = []


    def send(self, phylink):
        logging.debug(f"Sending packet from node:{self.id}")
        if not self.surrounding_node_list:
            nodes_in_range = get_nodes_in_range(self, param.range_mm)
        else:
            nodes_in_range = get_ap_if_in_range(self,param.range_mm)+self.surrounding_node_list
        self.tx_state = True
        time = ceil(get_transmit_time(phylink, param.throughput_bpstep))
        tx_add_stats(phylink)

        for node in nodes_in_range:
            self.env.process(node.start_rcv(phylink, time))

        yield self.env.timeout(time)

        self.tx_state = False

    def get_pos(self):
        return self.pos

    def start_rcv(self, phylink, transmition_time):
        if self.rx_on:
            if len(self.channel_resource.users) > self.concurrent_rec_limit:
                self.collision_bool = True
            else:
                self.collision_bool = False

            with self.channel_resource.request() as req:
                logging.debug(f" {self.id} Started receiving packet")
                # print(self.id, "Start receiving packet at ", self.env.now, "  receiving time:", transmition_time)
                yield self.env.timeout(transmition_time)
                self.recieve_phylink(phylink)

    def recieve_phylink(self, phylink):
        pass

    def recharge(self):
        while True:
            self.energy_lvl = param.battery_capacity
            # alternative is min(max_cap, curr_cap+recharge amount
            yield self.env.timeout(param.recharge_period)

    def setup_node_surrondings(self):
        self.surrounding_node_list = get_all_nodes_in_range(self, param.range_mm)


class Packet:
    size_list = None

    def __init__(self):
        self.packet_structure = None

    def unpack_bytearray(self, by: bytearray):

        i = 0
        for index, (key, _field) in enumerate(self.packet_structure.items()):
            _field = by[i:i + self.size_list[index]]

            if index < len(self.size_list) - 1:
                self.packet_structure[key] = int.from_bytes(_field, byteorder='big')
            else:
                _field = by[i:]
                self.packet_structure[key] = _field.decode('utf-8')

            i = i + self.size_list[index]

    def get_bytearray(self):
        arr = bytearray()

        for index, (key, _field) in enumerate(self.packet_structure.items()):

            if type(_field) is int:
                arr.extend(_field.to_bytes(self.size_list[index], byteorder='big'))
            else:
                arr.extend(bytearray(_field, 'utf-8'))

        return arr

    def get_parameters(self):
        """ get dictionary with parameter values"""
        return self.packet_structure

    def __str__(self):
        return str(self.get_parameters())


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
    if node not in param.simulated_nodes or distance_to_ap(node)>param.range_mm*3:
        return []
    x1, y1, z1 = node.get_pos()
    nodes_in_range = []
    for n2 in [n for n in param.simulated_nodes if n is not node]:
        x2, y2, z2 = n2.get_pos()
        if sqrt((((x2 - x1) ** 2) + ((y2 - y1) ** 2) + ((z2 - z1) ** 2))) <= max_range:
            nodes_in_range.append(n2)
    return nodes_in_range


def get_ap_if_in_range(node: Node, max_range: float):
    x1, y1, z1 = node.get_pos()
    ap = param.all_nodes[0]
    x2, y2, z2 = ap.get_pos()
    if 0 < sqrt((((x2 - x1) ** 2) + ((y2 - y1) ** 2) + ((z2 - z1) ** 2))) <= max_range:
        return [ap]
    return []

def get_all_nodes_in_range(node: Node, max_range: float):
    x1, y1, z1 = node.get_pos()
    nodes_in_range = []
    for n2 in [n for n in param.all_nodes if n is not node]:
        x2, y2, z2 = n2.get_pos()
        if sqrt((((x2 - x1) ** 2) + ((y2 - y1) ** 2) + ((z2 - z1) ** 2))) <= max_range:
            nodes_in_range.append(n2)
    return nodes_in_range

def distance_to_ap(node):
    x1,y1,z1 = param.all_nodes[0].get_pos()
    x2,y2,z2 = node.get_pos()
    return sqrt((((x2 - x1) ** 2) + ((y2 - y1) ** 2) + ((z2 - z1) ** 2)))


def get_transmit_time(phylink: PhyLink, throughput):
    # returns num of steps to complete transmition
    return phylink.bit_size() / throughput


def tx_add_stats(phylink):
    param.stats.stats_dir['transmitted_packets'] += 1
    param.stats.stats_dir['transmitted_bits'] += phylink.bit_size()


def rx_add_stats(phylink):
    param.stats.stats_dir['received_packets'] += 1
    param.stats.stats_dir['received_bits'] += phylink.bit_size()

def rx_add_data_stats(phylink):
    param.stats.stats_dir['received_data_packets'] += 1
    param.stats.stats_dir['received_data_bits'] += phylink.bit_size()

def send_data(node, **kwargs):
    packet = kwargs['packet']
    ph = PhyLink(packet.get_bytearray())
    yield node.env.timeout(1)
    node.env.process(node.send(ph))
