import string, random

from core_simulator.base_classes import Node, Frame, rx_add_stats, send_data, rx_add_data_stats
from core_simulator.functions import *


class RA_Node(Node):
    def __init__(self, env, node_id=1, position=(0, 0, 0), start_delay=0, is_relevant=True):
        super().__init__(env, node_id=node_id, position=position, is_relevant=is_relevant)

        self.env.process(self.periodically_send_data(start_delay))

    def periodically_send_data(self, start_delay):
        yield self.env.timeout(start_delay)
        while True:
            yield self.env.timeout(param.ra_data_interval)
            if check_buffer(self) and (not self.tx_state) and \
                    self.energy_lvl >= (param.ra_data_limit * 8 + param.data_overhead) * param.energy_bit_consumption:
                logging.debug(f"{self.id} sending data")
                self.env.process(send_data(self, packet=get_packet_from_buffer(self)))


class RA_AP(Node):
    def __init__(self, env, node_id=1):
        super().__init__(env, node_id, position=[0, 0, 0])
        self.rx_on = True

    def receive_phylink(self, phylink):
        if self.collision_bool:
            param.stats.stats_dir['collisions'] += 1
            logging.warning(f"{self.id}: collision at {self.env.now}")
            logging.debug(f'{self.id}: failed to receive packet')
        else:
            process_packet(self, phylink)


class DATAFrame(Frame):
    size_packet_type = 1
    size_payload = param.ra_data_limit
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


def process_packet(node: Node, packet):
    rx_add_stats(packet)
    data_packet = DATAFrame(packet.payload)
    logging.info(f"{node.id} data packet received successfully:{data_packet.packet_structure['payload']}")
    rx_add_data_stats(packet)


def periodically_add_data(node):
    data_packet = DATAFrame()
    data_packet.set_parameters(0, ''.join(random.choice(string.ascii_lowercase) for i in range(param.ra_data_limit)))
    while True:
        yield node.env.timeout(param.time_gen_function(*param.time_gen_limits))
        if len(node.send_buffer) >= param.buffer_size:
            node.send_buffer.pop(0)
        node.send_buffer.append(data_packet)
