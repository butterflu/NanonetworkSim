from dataclasses import dataclass, field
from math import ceil, sqrt
from functions import *
import numpy
import simpy
import logging

import binascii
from parameters import *

if use_rih:
    from MAC_protocol.RIH import *


class Node:
    def __init__(self, env, node_id=1, position=(0, 0), start_delay=0):
        if position is None:
            position = [0, 0]
        self.env = env
        self.channel_resource = simpy.Resource(env, capacity=1)
        self.pos = [0, 0]  # x, y
        self.id = node_id
        self.concurrent_rec_limit = rec_limit
        self.collision_bool = False  # for colission detection
        self.tx_state = False  # for marking if outbound tx is in progress
        self.rx_on = False  # to mark when receiving is on
        self.send_buffer = []
        # energy is expressed as number of bytes able to send rather than any standard energy unit
        self.energy_lvl = 64

        self.env.process(self.recharge())
        self.env.process(self.rxon_cycle(start_delay))

    # TODO add battery limitation

    def send(self, phylink):
        logging.debug(f"Sending packet from node:{self.id}")
        nodes_in_range = get_nodes_in_range(self, range_mm)
        self.tx_state = True
        time = get_transmit_time(phylink, throughput_mbpstep)
        # print(time, "-time")
        time = ceil(time)

        # print(self.id, "send packet at", self.env.now)
        tx_add_stats(phylink)

        for node in nodes_in_range:
            self.env.process(node.start_rcv(phylink, time))

        yield self.env.timeout(time)
        self.tx_state = False

    def get_pos(self):
        return self.pos

    def start_rcv(self, phylink, transmition_time):
        # if self.rx_on:
            if len(self.channel_resource.users) > self.concurrent_rec_limit:
                self.collision_bool = True
            else:
                self.collision_bool = False

            with self.channel_resource.request() as req:
                logging.debug(f" {self.id} Started receiving packet")
                # print(self.id, "Start receiving packet at ", self.env.now, "  receiving time:", transmition_time)
                yield self.env.timeout(transmition_time)
                self.recieve_phylink(phylink)

        # else:
        #     logging.debug(f"{self.id}: skipped packet as rx is not on")

    def recieve_phylink(self, phylink):
        packet_type = phylink.payload[0]
        self.energy_lvl -= ceil(phylink.bit_size() / 10)
        if (self.collision_bool or self.tx_state) and packet_type == 0 and self.rx_on == True:
            stats.collisions += 1
            logging.warning(f"{self.id}: colision at {self.env.now}")
            logging.debug(f'{self.id}: failed to receive packet')
        else:
            process_packet(self, phylink, packet_type)

    def rxon_cycle(self, start_delay):
        yield self.env.timeout(start_delay)
        while True:
            yield self.env.timeout(param.steps_in_s - param.rxon_duration)
            self.rx_on = True
            self.energy_lvl -= param.rxon_duration / 10 * step / 10 ** -5

            yield self.env.timeout(param.rxon_duration)

    # TODO battery balance update
    def recharge(self):
        while True:
            self.energy_lvl = battery_capacity
            # alternative is min(max_cap, curr_cap+recharge amount
            yield self.env.timeout(recharge_period)


class AP(Node):
    def __init__(self, env, node_id=1):
        super().__init__(env, node_id)
        self.env.process(self.periodically_send_rtr())
        self.rx_on = True

    def send_broadcast_rtr(self):
        logging.info(f"{self.id}: sending broadcast rtr at {self.env.now}")
        rtr_packet = RTRPacket()
        rtr_packet.set_parameters(1)
        pl = PhyLink(rtr_packet.get_bytearray())
        self.env.process(self.send(pl))
        stats.transmitted_rtr += 1

    def periodically_send_rtr(self):
        while True:
            yield self.env.timeout(rtr_interval)
            if not self.tx_state:
                self.send_broadcast_rtr()

    def rxon_cycle(self, start_delay):
        yield self.env.timeout(0)


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
    # print(nodes_in_range)
    return nodes_in_range


def get_dist_between_nodes(node1: Node, node2: Node):
    x1, y1 = node1.get_pos()
    x2, y2 = node2.get_pos()
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5


def get_transmit_time(phylink: PhyLink, throughput):
    # returns num of steps to complete transmition
    return phylink.bit_size() / throughput * 1000


# temp function
def periodically_add_data(node: Node):
    data_packet = DATAPacket()
    data_packet.set_parameters(0, "data")
    while True:
        yield node.env.timeout(time_gen_function(*time_gen_limits))
        if len(node.send_buffer) >= buffer_size:
            node.send_buffer.pop(0)
        node.send_buffer.append(data_packet)
