import string, random, math

from core_simulator.base_classes import Node, PhyLink, Frame, rx_add_stats, send_data, rx_add_data_stats
from core_simulator.functions import *


# class to set if RTR method is used
class TW_Node(Node):
    def __init__(self, env, node_id=1, position=(0, 0, 0), start_delay=0, is_relevant=True):
        super().__init__(env, node_id=node_id, position=position, is_relevant=is_relevant)
        self.rx_on = False  # to mark when receiving is on

        self.env.process(self.periodically_send_hello(start_delay))

    def send_broadcast_hello(self):
        if math.floor((self.energy_lvl - param.energy_for_processing - 10) / param.energy_bit_consumption / 8) < 1:
            logging.warning(f" node {self.id} skipped hello frame")
            # skip if energy is below critical
            return
        logging.debug(f"{self.id}: sending broadcast hello at {self.env.now}")
        hello_packet = HelloFrame()
        pl = PhyLink(hello_packet.get_bytearray())
        self.env.process(self.send(pl))
        param.stats.stats_dir['transmitted_hello'] += 1
        self.env.process(self.turn_rx_on(param.tw_rtr_listening_time))

    def periodically_send_hello(self, start_delay):
        yield self.env.timeout(start_delay)
        while True:
            yield self.env.timeout(param.tw_hello_interval)
            self.send_broadcast_hello()

    def turn_rx_on(self, steps_num):
        self.rx_on = True
        self.energy_lvl -= steps_num * 64 * param.energy_bit_consumption / 10
        # param.temp_batterytracker[str(self.id)].append(self.energy_lvl)
        yield self.env.timeout(steps_num)
        self.rx_on = False

    def receive_phylink(self, phylink):
        packet_type = phylink.payload[0]
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

    def receive_phylink(self, phylink):
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
        rtr_packet = RTRFrame()
        pl = PhyLink(rtr_packet.get_bytearray())
        self.env.process(self.send(pl))
        param.stats.stats_dir['transmitted_rtr'] += 1

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


class HelloFrame(Frame):
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


class RTRFrame(Frame):
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

        # hello_packet = HelloFrame(packet.payload)
        param.stats.stats_dir['received_hello'] += 1

        if not node.tx_state and node.rx_on:
            logging.info(f"{node.id} sending rtr response")
            node.hello_response()

    elif packet_type == 1:
        # rtr_packet = RTRFrame(packet.payload)
        param.stats.stats_dir['received_rtr'] += 1
        print(node.tx_state)
        if node.tx_state:
            # -1 for header, 10 extra fJ reserved
            resp_dyn_payload = math.floor(
                (node.energy_lvl - param.energy_for_processing - 10) / param.energy_bit_consumption / 8) - 1

            print(resp_dyn_payload)

            logging.info(f"{node.id} sending data")
            node.env.process(send_data(node, packet=create_data_packet(resp_dyn_payload)))

    else:
        data_packet = DATAFrame(packet.payload)

        if type(node) is TW_AP:
            logging.info(f"{node.id} data packet received successfully:{data_packet.packet_structure['payload']}")
            rx_add_data_stats(packet)
        else:
            logging.debug('Received DATA not by AP')


def create_data_packet(size):
    data_packet = DATAFrame()
    data_packet.set_parameters(0, ''.join(random.choice(string.ascii_lowercase) for i in range(size)))
    return data_packet
