from dataclasses import dataclass
import csv

@dataclass
class Stats():
    def __init__(self):
        self.transmitted_bits = 0
        self.transmitted_packets = 0
        self.received_bits = 0
        self.received_packets = 0
        self.collisions = 0
        self.transmitted_rtr = 0
        self.received_rtr = 0

    def get_stats(self):
        out = []
        out.append('transmitted_bits:')
        out.append(self.transmitted_bits)
        out.append('transmitted_packets:')
        out.append(self.transmitted_packets)
        out.append('received_bits:')
        out.append(self.received_bits)
        out.append('received_packets:')
        out.append(self.received_packets)
        out.append('collisions:')
        out.append(self.collisions)
        out.append('transmitted_rtr:')
        out.append(self.transmitted_rtr)
        out.append('received_rtr:')
        out.append(self.received_rtr)
        out.append('received_DATA_packets:')
        out.append(self.received_packets - self.received_rtr)
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
