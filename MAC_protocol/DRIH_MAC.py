class RTRPacket:
    # size in bytes
    size_packet_sequence_id = 2
    size_node_id = 2
    size_destination_id = 2
    size_num_of_nei = 1
    size_max_degree = 1
    size_energy_lvl = 2
    size_comm_mode = 1
    size_ack = 3
    size_link_color = 1
    size_rot_offset_num = 2
    size_payload = 7
    size_list = [size_packet_sequence_id, size_node_id, size_destination_id, size_num_of_nei, size_max_degree,
                 size_energy_lvl, size_comm_mode, size_ack, size_link_color, size_rot_offset_num, size_payload]

    def __init__(self, byte_arr=None):
        self.packet_structure = {
            "packet_sequence_id": None,
            "node_id": None,
            "destination_id": None,
            "num_of_nei": None,
            "max_degree": None,
            "energy_lvl": None,
            "comm_mode": None,
            "ack": None,
            "link_color": None,
            "rot_offset_num": None,
            "payload": None
        }
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

    def set_parameters(self, packet_sequence_id, node_id, destination_id, num_of_nei, max_degree, energy_lvl, comm_mode,
                       ack, link_color, rot_offset_num, payload):
        """ Function used to set fields of RTR packet """
        self.packet_structure["packet_sequence_id"] = packet_sequence_id
        self.packet_structure["node_id"] = node_id
        self.packet_structure["destination_id"] = destination_id
        self.packet_structure["num_of_nei"] = num_of_nei
        self.packet_structure["max_degree"] = max_degree
        self.packet_structure["energy_lvl"] = energy_lvl
        self.packet_structure["comm_mode"] = comm_mode
        self.packet_structure["ack"] = ack
        self.packet_structure["link_color"] = link_color
        self.packet_structure["rot_offset_num"] = rot_offset_num
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


if __name__ == "__main__":
    rtr_paket = RTRPacket()
    rtr_paket.set_parameters(15, 1, 1, 1, 1, 5, 2, 1, 0, 12, '2345678345678')
    print(rtr_paket.get_parameters())
    b = rtr_paket.get_bytearray()
    print(b)
    rtr = RTRPacket(b)
    print(rtr.get_parameters())
