import logging

import parameters as param
import csv
# from stats import Stats
import matplotlib.pyplot as plt


def get_nodes_position():
    positions = [[], [], []]
    for node in param.all_nodes:
        x, y, z = node.get_pos()
        positions[0].append(x)
        positions[1].append(y)
        positions[2].append(z)

    return positions


# temp function

def check_buffer(node):
    if len(node.send_buffer) >= 1:
        return True
    else:
        return False


def get_packet_from_buffer(node):
    if check_buffer(node):
        packet = node.send_buffer[0]
        node.send_buffer.remove(packet)
        return packet


def prepare_csv(name="stats"):
    filename = name + '.csv'
    f = open(filename, 'w')
    csv_writer = csv.writer(f)

    # parameters
    parameters = [
        'use_rih',
        'use_ra',
        'use_2way',
        'step',
        'battery_capacity',
        'rtr_interval_s',
        'rih_data_limit',
        'ra_data_limit',
        'ra_data_interval',
        'data_overhead',
        'velocity_cmps',
        'vein_diameter_mm',
        'nodes_num',
        'sim_time_s',
        'stats_collection_time'

    ]

    csv_writer.writerow(parameters + param.stats.get_stats())
    f.close()


def append_csv(name="stats"):
    filename = name + '.csv'
    f = open(filename, 'a')
    csv_writer = csv.writer(f)

    parameters_val = [
        param.use_rih,
        param.use_ra,
        param.use_2way,
        param.step,
        param.battery_capacity,
        param.rtr_interval_s,
        param.rih_data_limit,
        param.ra_data_limit,
        param.ra_data_interval,
        param.data_overhead,
        param.velocity_cmps,
        param.vein_diameter_mm,
        param.nodes_num,
        param.sim_time_s,
        (param.stats_timer[1] - param.stats_timer[0]) / param.steps_in_s
    ]

    csv_writer.writerow(parameters_val + param.stats.get_stats_value())
    f.close()


def clear_sim():
    param.all_nodes.clear()
    param.simulated_nodes.clear()
    param.stats.reset_stats()


def clear_stats(env):
    yield env.timeout(param.startup_time * param.steps_in_s)
    param.stats.reset_stats()
    param.stats_timer[0] = env.now
    logging.debug(f'Start collecting stats at {env.now}')


def show_xz_coords(horizontal_lines=[]):
    x, y, z = get_nodes_position()
    c = []
    ap_pos = param.all_nodes[0].get_pos()
    plt.plot(ap_pos[0], ap_pos[2], marker='o', markersize=10)

    for node in param.all_nodes:
        if node in param.simulated_nodes:
            c.append('g')
        elif node.is_relevant:
            c.append('b')
        else:
            c.append('brown')

    plt.scatter(x, z, s=0.3, c=c)
    for line in horizontal_lines:
        plt.axvline(x=line, color='r')
    plt.show()


def plot_battery_life(battery_tracker: dict):
    fig, ax = plt.subplots()
    for key in battery_tracker:
        # if (int(key) % 100) == 1:
            row = battery_tracker[key]
            ax.plot(range(0, len(row)), row)
            # print(key, len(row))

    plt.show()
