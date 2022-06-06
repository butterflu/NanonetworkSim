import logging

from core_simulator.base_classes import Node, PhyLink, stats
import core_simulator.parameters as param
from core_simulator.functions import rx_add_stats


class DATAPacket:
    size_packet_type = 1
    size_payload = param.RIH_data_payload_limit
    size_list = [size_packet_type, size_payload]

    def __init__(self, byte_arr=None):
        self.packet_structure = {
            "packet_type": None,
            "payload": None
        }
        # packet type 0 - data, 1 - RTR
        if byte_arr:
            self.unpack_bytearray(byte_arr)

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

    def set_parameters(self, packet_type, payload):
        """ Function used to set fields of RTR packet """
        self.packet_structure["packet_type"] = packet_type
        self.packet_structure["payload"] = payload

    def get_parameters(self):
        """ get dictionary with parameter values"""
        return self.packet_structure

    def get_bytearray(self):
        arr = bytearray()

        for index, (key, _field) in enumerate(self.packet_structure.items()):

            if type(_field) is int:
                arr.extend(_field.to_bytes(self.size_list[index], byteorder='big'))
            else:
                arr.extend(bytearray(_field, 'utf-8'))

        return arr

    def __str__(self):
        return str(self.get_parameters())


class RTRPacket:
    # size in bytes
    size_packet_type = 1
    size_list = [size_packet_type]

    def __init__(self, byte_arr=None):
        self.packet_structure = {
            "packet_type": None
        }
        # packet type 0 - data, 1 - RTR
        if byte_arr:
            self.unpack_bytearray(byte_arr)

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

    def set_parameters(self, packet_type):
        """ Function used to set fields of RTR packet """
        self.packet_structure["packet_type"] = packet_type

    def get_parameters(self):
        """ get dictionary with parameter values"""
        return self.packet_structure

    def get_bytearray(self):
        arr = bytearray()

        for index, (key, _field) in enumerate(self.packet_structure.items()):

            if type(_field) is int:
                arr.extend(_field.to_bytes(self.size_list[index], byteorder='big'))
            else:
                arr.extend(bytearray(_field, 'utf-8'))

        return arr

    def __str__(self):
        return str(self.get_parameters())


def process_packet(node: Node, packet, packet_type):
    # print(node.id, "processing packet at", node.env.now)
    rx_add_stats(packet)
    if packet_type == 1:
        rtr_packet = RTRPacket(packet.payload)

        print(node.id, "received RTR packet:")
        stats.received_rtr += 1

        # TODO energy lvl requires correction
        if check_buffer(node) and (not node.tx_state) and node.energy_lvl >= 64:
            print(node.id, "sending data")
            node.env.process(send_data(node, packet=get_packet_from_buffer(node)))

        else:
            logging.error('Error in processing RTR packet')
            return

    else:
        data_packet = DATAPacket(packet.payload)

        if data_packet.packet_structure["destination_id"] == node.id:
            print(node.id, " data packet received successfully:", data_packet.packet_structure["payload"])
        else:
            logging.debug('Received DATA packet to another node')
            pass


def check_buffer(node: Node):
    if len(node.send_buffer) >= 1:
        return True
    else:
        return False


def get_packet_from_buffer(node: Node):
    if check_buffer(node):
        packet = node.send_buffer[0]
        node.send_buffer.remove(packet)
        return packet


def send_data(node: Node, **kwargs):
    packet = kwargs['packet']
    ph = PhyLink(packet.get_bytearray())
    yield node.env.timeout(1)
    node.env.process(node.send(ph))


def send_RTR(node, dst_id=2):
    seq = 1
    rtr_packet = RTRPacket()
    rtr_packet.set_parameters(1, seq, node.id, dst_id, 0, 0, 1, 0, 0, 0, 0, "payload")
    node.env.process(node.send(PhyLink(rtr_packet.get_bytearray())))


if __name__ == "__main__":
    rtr_paket = RTRPacket()
    rtr_paket.set_parameters(15, 1, 1, 1, 1, 5, 2, 1, 0, 12, '2345657')

    print(rtr_paket.get_parameters())
    b = rtr_paket.get_bytearray()
    print(len(b))
    rtr = RTRPacket(b)
    print(rtr.get_parameters())
