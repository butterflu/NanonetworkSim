import math
import string, random

from core_simulator.base_classes import Node, PhyLink, Frame, rx_add_stats, send_data, rx_add_data_stats
from core_simulator.functions import *


class RTR_Node(Node):
    def __init__(self, env, node_id=1, position=(0, 0, 0), start_delay=0, is_relevant=True):
        super().__init__(env, node_id=node_id, position=position, is_relevant=is_relevant)

        self.rx_on = False  # to mark when receiving is on
        if is_relevant:
            self.env.process(self.rxon_cycle(start_delay))

    def rxon_cycle(self, start_delay):
        yield self.env.timeout(start_delay)
        while True:
            yield self.env.timeout(param.steps_in_s - param.rxon_duration)
            self.rx_on = True
            self.energy_lvl -= param.rxon_duration * 64 * param.energy_bit_consumption / 10
            # param.temp_batterytracker[str(self.id)].append(self.energy_lvl)
            yield self.env.timeout(param.rxon_duration)

            self.rx_on = False

    def receive_phylink(self, phylink):
        packet_type = phylink.payload[0]
        if self.tx_state:
            logging.debug(f'{self.id}: received packet during transmission')
        elif self.collision_bool:
            param.stats.stats_dir['collisions'] += 1
            logging.warning(f"{self.id}: colision at {self.env.now}")
            logging.debug(f'{self.id}: failed to receive packet')
        else:
            process_packet(self, phylink, packet_type)


class RTR_AP(Node):
    def __init__(self, env, node_id=1):
        super().__init__(env, node_id, position=[0, 0, 0])
        self.env.process(self.periodically_send_rtr())
        self.rx_on = True

    def send_broadcast_rtr(self):
        if len(self.channel_resource.users) > 0:
            # skip if receiving
            return
        # logging.info(f"{self.id}: sending broadcast rtr at {self.env.now}")
        rtr_packet = RTRFrame()
        rtr_packet.set_parameters(1)
        pl = PhyLink(rtr_packet.get_bytearray())
        self.env.process(self.send(pl))
        param.stats.stats_dir['transmitted_rtr'] += 1

    def periodically_send_rtr(self):
        while True:
            yield self.env.timeout(param.rtr_interval)
            self.send_broadcast_rtr()

    def receive_phylink(self, phylink):
        packet_type = phylink.payload[0]
        if self.collision_bool or self.tx_state:
            param.stats.stats_dir['collisions'] += 1
            logging.warning(f"{self.id}: colision at {self.env.now}")
            logging.debug(f'{self.id}: failed to receive packet')
        else:
            process_packet(self, phylink, packet_type)

    def recharge(self):
        pass


class DATAFrame(Frame):
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


class RTRFrame(Frame):
    # size in bytes
    size_packet_type = 1
    size_list = [size_packet_type]

    def __init__(self, byte_arr=None):
        super().__init__()
        self.packet_structure = {
            "packet_type": None
        }
        # packet type 0 - data, 1 - RTR
        if byte_arr:
            self.unpack_bytearray(byte_arr)

    def set_parameters(self, packet_type):
        """ Function used to set fields of RTR packet """
        self.packet_structure["packet_type"] = packet_type


def process_packet(node: Node, packet, packet_type):
    rx_add_stats(packet)
    if packet_type == 1:
        # rtr_packet = RTRFrame(packet.payload)
        # print(node.id, "received RTR packet:")
        param.stats.stats_dir['received_rtr'] += 1
        if not node.tx_state:
            # -1 for header, 100fJ reservation for preservation of functionality
            resp_dyn_payload = math.floor(
                (node.energy_lvl - param.energy_for_processing - 10) / param.energy_bit_consumption / 8) - 1
            print(resp_dyn_payload)

            logging.info(f"{node.id} sending data")
            node.env.process(send_data(node, packet=create_data_packet(resp_dyn_payload)))

    else:
        data_packet = DATAFrame(packet.payload)

        if type(node) is RTR_AP:
            logging.info(f"{node.id} data packet received successfully:{data_packet.packet_structure['payload']}")
            rx_add_data_stats(packet)
        else:
            logging.debug('Received DATA not by AP')


def create_data_packet(size):
    data_packet = DATAFrame()
    data_packet.set_parameters(0, ''.join(random.choice(string.ascii_lowercase) for i in range(size)))
    return data_packet
