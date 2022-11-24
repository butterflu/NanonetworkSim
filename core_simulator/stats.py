class Stats():
    stats_dir = {
        'transmitted_bits': 0,
        'transmitted_packets': 0,
        'received_bits': 0,
        'received_packets': 0,
        'collisions': 0,
        'transmitted_rtr': 0,
        'received_rtr': 0,
        'transmitted_hello': 0,
        'received_hello': 0,
        'received_data_packets': 0,
        'received_data_bits': 0
    }

    def __init__(self):
        self.reset_stats()

    def get_stats(self):
        out = []

        for key, _field in self.stats_dir.items():
            out.append(key + ':')

        return out

    def get_stats_value(self):
        out = []
        for key, _field in self.stats_dir.items():
            out.append(_field)

        return out

    def print_stats(self):
        print(self.get_stats())

    def reset_stats(self):
        self.stats_dir = {
            'transmitted_bits': 0,
            'transmitted_packets': 0,
            'received_bits': 0,
            'received_packets': 0,
            'collisions': 0,
            'transmitted_rtr': 0,
            'received_rtr': 0,
            'transmitted_hello': 0,
            'received_hello': 0,
            'received_data_packets': 0,
            'received_data_bits': 0
        }