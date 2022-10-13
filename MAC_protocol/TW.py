import string, random

from core_simulator.base_classes import Node, PhyLink, Packet, rx_add_stats, send_data, rx_add_data_stats
from core_simulator.functions import *


# class to set if RTR method is used
class TW_Node(Node):
    def __init__(self, env, node_id=1, position=(0, 0, 0), start_delay=0, is_relevant=True):
        super().__init__(env, node_id=node_id, position=position, is_relevant=is_relevant)
        self.rx_on = False  # to mark when receiving is on

        self.env.process(self.periodically_send_hello(start_delay))

    def send_broadcast_hello(self):
        # logging.debug(f"{self.id}: sending broadcast hello at {self.env.now}")
        hello_packet = HelloPacket()
        pl = PhyLink(hello_packet.get_bytearray())
        yield self.env.process(self.send(pl))
        param.stats.stats_dir['transmitted_hello'] += 1
        self.env.process(self.turn_rx_on(param.tw_rtr_listening_time))

    def periodically_send_hello(self, start_delay):
        yield self.env.timeout(start_delay)
        while True:
            yield self.env.timeout(param.tw_hello_interval)
            self.env.process(self.send_broadcast_hello())

    def turn_rx_on(self, steps_num):
        # print('rxon', self.env.now)
        self.rx_on = True
        self.energy_lvl -= steps_num / 10*64
        yield self.env.timeout(steps_num)
        self.rx_on = False
        # print('rxoff', self.env.now)

    def recieve_phylink(self, phylink):
        packet_type = phylink.payload[0]
        # print('received packet', self.env.now)
        if self.tx_state:
            logging.warning(f'{self.id}: received packet during transmission')
        elif self.collision_bool:
            param.stats.stats_dir['collisions'] += 1
            logging.warning(f"{self.id}: colision at {self.env.now}")
        else:
            process_packet(self, phylink, packet_type)



class TW_AP(Node):
    def __init__(self, env, node_id=1):
        super().__init__(env, node_id, position=[0, 0, 0])
        self.rx_on = True

    def recieve_phylink(self, phylink):
        packet_type = phylink.payload[0]
        if self.tx_state:
            logging.warning(f'{self.id}: received packet during transmission')
        elif self.collision_bool:
            param.stats.stats_dir['collisions'] += 1
            logging.warning(f"{self.id}: colision at {self.env.now}")
            logging.debug(f'{self.id}: failed to receive packet')
        else:
            process_packet(self, phylink, packet_type)

    def hello_response(self):
        rtr_packet = RTRPacket()
        pl = PhyLink(rtr_packet.get_bytearray())
        #processing delay
        yield self.env.timeout(0.1)
        self.env.process(self.send(pl))
        param.stats.stats_dir['transmitted_rtr'] += 1
        # print('rtr sent at ', self.env.now)


class DATAPacket(Packet):
    size_packet_type = 1
    size_payload = param.rih_data_limit
    size_list = [size_packet_type, size_payload]

    def __init__(self, byte_arr=None):
        super().__init__()
        self.packet_structure = {
            "packet_type": None,
            "payload": None
        }
        # packet type 0 - data, 1 - RTR
        if byte_arr:
            self.unpack_bytearray(byte_arr)

    def set_parameters(self, packet_type, payload):
        """ Function used to set fields of RTR packet """
        self.packet_structure["packet_type"] = packet_type
        self.packet_structure["payload"] = payload


class HelloPacket(Packet):
    # size in bytes
    size_packet_type = 1
    size_list = [size_packet_type]

    def __init__(self, byte_arr=None):
        super().__init__()
        self.packet_structure = {
            "packet_type": None
        }
        # packet type 0 - data, 1 - Hello, 2 - RTR
        if byte_arr:
            self.unpack_bytearray(byte_arr)
        else:
            self.packet_structure["packet_type"] = 2

    def set_parameters(self, packet_type):
        """ Function used to set fields of Hello packet """
        self.packet_structure["packet_type"] = packet_type


class RTRPacket(Packet):
    # size in bytes
    size_packet_type = 1
    size_list = [size_packet_type]

    def __init__(self, byte_arr=None):
        super().__init__()
        self.packet_structure = {
            "packet_type": None
        }
        # packet type 0 - data, 1 - Hello, 2 - RTR
        if byte_arr:
            self.unpack_bytearray(byte_arr)
        else:
            self.packet_structure["packet_type"] = 1

    def set_parameters(self, packet_type):
        """ Function used to set fields of RTR packet """
        self.packet_structure["packet_type"] = packet_type


def process_packet(node, packet, packet_type):
    rx_add_stats(packet)
    if packet_type == 2:
        if type(node) is TW_Node:
            # logging.warning('node received hello packet')
            return

        # hello_packet = HelloPacket(packet.payload)
        param.stats.stats_dir['received_hello'] += 1

        if not node.tx_state and node.rx_on:
            logging.info(f"{node.id} sending rtr response at {node.env.now}")
            node.env.process(node.hello_response())

    elif packet_type == 1:
        # rtr_packet = RTRPacket(packet.payload)
        param.stats.stats_dir['received_rtr'] += 1
        # print(f'rtr  received, {node.tx_state}, {node.rx_on}')
        if check_buffer(node) and (
                not node.tx_state) and node.energy_lvl >= param.tw_data_limit * 8 + param.data_overhead:
            logging.info(f"{node.id} sending data")
            node.env.process(send_data(node, packet=get_packet_from_buffer(node)))

    else:
        data_packet = DATAPacket(packet.payload)

        if type(node) is TW_AP:
            logging.info(f"{node.id} data packet received successfully:{data_packet.packet_structure['payload']}")
            rx_add_data_stats(packet)
        else:
            logging.debug('Received DATA not by AP')


def periodically_add_data(node):
    data_packet = DATAPacket()
    data_packet.set_parameters(0, ''.join(random.choice(string.ascii_lowercase) for i in range(param.ra_data_limit)))
    while True:
        yield node.env.timeout(param.time_gen_function(*param.time_gen_limits))
        if len(node.send_buffer) >= param.buffer_size:
            node.send_buffer.pop(0)
        node.send_buffer.append(data_packet)
