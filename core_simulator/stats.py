from dataclasses import dataclass
import csv


@dataclass
class Stats():
    def __init__(self):
        self.stats_dir = {
            'transmitted_bits': 0,
            'transmitted_packets': 0,
            'received_bits': 0,
            'received_packets': 0,
            'collisions': 0,
            'transmitted_rtr': 0,
            'received_rtr': 0,
            'transmitted_hello': 0,
            'received_hello': 0
        }

    def get_stats(self):
        out = []

        for key, _field in self.stats_dir.items():
            out.append(key+':')
            out.append(_field)

        out.append('received_DATA_packets:')
        out.append(self.stats_dir['received_packets'] - self.stats_dir['received_rtr'] - self.stats_dir['received_hello'])

        return out

    def print_stats(self):
        print(self.get_stats())

    def save_stats_to_file(self, name="stats"):
        filename = name + '.txt'
        f = open(filename, 'w')
        for line in self.get_stats():
            f.write(str(line))
        f.close()

    def save_csv(self, name="stats"):
        filename = name + '.csv'
        f = open(filename, 'w')
        csv_writer = csv.writer(f)

        s = self.get_stats()
        var_names = [s[x] for x in range(len(s)) if x % 2 == 0]
        var_value = [s[x] for x in range(len(s)) if x % 2 == 1]
        csv_writer.writerow(var_names)
        csv_writer.writerow(var_value)

        f.close()
