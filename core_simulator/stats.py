transmitted_bits = 0
transmitted_packets = 0

received_bits = 0
received_packets = 0

collisions = 0

transmitted_rtr = 0
received_rtr = 0


def print_stats():
    out = []
    out.append('\ntransmitted_bits:')
    out.append(transmitted_bits)
    out.append('\ntransmitted_packets:')
    out.append(transmitted_packets)
    out.append('\nreceived_bits:')
    out.append(received_bits)
    out.append('\nreceived_packets:')
    out.append(received_packets)
    out.append('\ncollisions:')
    out.append(collisions)
    out.append('\ntransmitted_rtr:')
    out.append(transmitted_rtr)
    out.append('\nreceived_rtr:')
    out.append(received_rtr)
    print(out)
