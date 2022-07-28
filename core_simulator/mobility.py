from numpy.random import uniform, binomial, dirichlet
import parameters as param
import numpy as np
from simpy import Environment
import logging
from functions import clear_stats, show_xz_coords

"""
For 1 node setup, ap-node is in 0;0     for multi ap-node setup, y is set in 0

-------negative x values--------ap-node(0;0)-----------positive x values-----------z=0
        o    .      o       o           o       .    o           o       O                   ↗
       O     o           o      .             o           o               O               Y
  o         o   o       o     O      o       .    o           o       o    .           ↙
-----------------------------------------------------------------------------------z=vein diameter

X - along the vein
Y - width (depth)
Z - height
 
All x,y values are in mm
"""


# move all nodes to the right (or ap to the left as all movement is relative)

def move_ap(env: Environment, ap):
    logging.info('Starting ap mobility ...')
    while True:
        yield env.timeout(1)
        ap.pos[0] = ap.pos[0] - param.velocity_mmps * param.step


def setup_segment(env: Environment, x_range: list, segment_nodes: int, nodes_id: int):
    if param.use_rih:
        from MAC_protocol.RIH import RTR_Node, RTR_AP, periodically_add_data
    elif param.use_ra:
        from MAC_protocol.RA import RA_AP, RA_Node, periodically_add_data
    elif param.use_2way:
        from MAC_protocol.TW import TW_AP, TW_Node, periodically_add_data
    else:
        print("no mode selected")
        exit(-1)

    logging.debug(f'Segment setup: nodes_num:{segment_nodes}, xrange:{x_range}, start_id:{nodes_id}')

    x_start = x_range[0]
    x_end = x_range[1]

    # randomize positions, using polar coordinates to distribute uniformly
    r = np.multiply(param.vein_diameter_mm / 2, np.sqrt(uniform(size=segment_nodes)))
    theta = uniform(0, 2 * np.pi, size=segment_nodes)
    y_values = r * np.sin(theta)
    z_values = r * np.cos(theta) + (param.vein_diameter_mm / 2)
    x_uniform = uniform(x_start, x_end, size=segment_nodes)
    x_values = [round(x, 3) for x in x_uniform]

    pos_combined = np.stack((x_values, y_values, z_values), axis=1)
    x1, y1, z1 = param.all_nodes[0].get_pos()

    for node_id, pos in zip(range(nodes_id, nodes_id + segment_nodes + 1), pos_combined):
        x2, y2, z2 = pos
        xaxis_dist = np.sqrt((((z2 - z1) ** 2) + ((y2 - y1) ** 2)))
        is_rel = xaxis_dist <= param.node_relevant_range
        if param.use_rih:
            node = RTR_Node(env=env, node_id=node_id, position=pos, start_delay=uniform(0, param.steps_in_s),
                            is_relevant=is_rel)
        elif param.use_ra:
            node = RA_Node(env=env, node_id=node_id, position=pos, start_delay=uniform(0, param.steps_in_s),
                           is_relevant=is_rel)
        elif param.use_2way:
            node = TW_Node(env=env, node_id=node_id, position=pos, start_delay=uniform(0, param.steps_in_s),
                           is_relevant=is_rel)

        env.process(periodically_add_data(node))
        param.all_nodes.append(node)
        if xaxis_dist <= param.sim_range:
            param.simulated_nodes.append(node)
        logging.debug(f"Added node id: {node_id}")


def segment_collector():
    """
    function to do a garbage collecting on useless nodes
    deletes all nodes past 3s*velocity_mmps
    """
    all_nodes = param.all_nodes[:]
    ap_pos = all_nodes[0].get_pos()
    for node in param.all_nodes:
        pos = node.get_pos()
        if pos[0] > (param.velocity_mmps * 3) + ap_pos[0]:
            all_nodes.remove(node)
            if node in param.simulated_nodes:
                param.simulated_nodes.remove(node)
    param.all_nodes = all_nodes


def manage_segments(env):

    num_simulated_nodes = int(param.sim_time_s * param.velocity_mmps / 100 * np.pi * (
            (param.vein_diameter_mm / 200) ** 2) / param.blood_volume_l * param.nodes_num)

    segments_num = int(np.floor((param.sim_time_s + param.startup_time / 2) / param.approx_segment_size_s))
    segment_size_s = (param.sim_time_s + param.startup_time / 2) / segments_num

    x_start = -np.ceil((param.sim_time_s + param.startup_time) * param.velocity_mmps)
    x_end = -param.startup_time / 2 * param.velocity_mmps
    x_ranges = np.append(np.arange(x_end, x_start, -segment_size_s * param.velocity_mmps), x_start)
    logging.info(f"Segment num: {segments_num}, size: {segment_size_s}, simulated_nodes: {num_simulated_nodes}")

    nodes_spread = [binomial(n=2 * n, p=param.p) for n in np.ones(segments_num)*num_simulated_nodes/segments_num]
    # print(nodes_spread)

    for segment_nr in range(segments_num):
        # show_xz_coords([x_ranges[segment_nr], x_ranges[segment_nr + 1],
        #                 (param.velocity_mmps * 3) + param.all_nodes[0].get_pos()[0]])

        setup_segment(env, x_range=[x_ranges[segment_nr], x_ranges[segment_nr + 1]],
                      segment_nodes=int(nodes_spread[segment_nr]),
                      nodes_id=int(sum(nodes_spread[0:segment_nr])))

        # show_xz_coords([x_ranges[segment_nr], x_ranges[segment_nr + 1],
        #                 (param.velocity_mmps * 3) + param.all_nodes[0].get_pos()[0]])

        yield env.timeout(segment_size_s * param.steps_in_s)
        segment_collector()

        # show_xz_coords([x_ranges[segment_nr], x_ranges[segment_nr + 1],
        #                 (param.velocity_mmps * 3) + param.all_nodes[0].get_pos()[0]])


def setup_nodes(env):
    """
    function to set up nodes and assign them to propper lists
    :return:
    """
    if param.use_rih:
        from MAC_protocol.RIH import RTR_AP
    elif param.use_ra:
        from MAC_protocol.RA import RA_AP
    elif param.use_2way:
        from MAC_protocol.TW import TW_AP
    else:
        print("no mode selected")
        exit(-1)

    print(f'nodes_num:{param.nodes_num}, ra:{param.use_ra}, rih:{param.use_rih},  2way:{param.use_2way}')
    logging.info('Starting node setup ...')

    # add nano-router
    if param.use_rih:
        ap = RTR_AP(env=env, node_id=1)
    elif param.use_ra:
        ap = RA_AP(env=env, node_id=1)
    elif param.use_2way:
        ap = TW_AP(env=env, node_id=1)

    param.all_nodes.append(ap)
    param.simulated_nodes.append(ap)

    # segment setup process

    env.process(manage_segments(env))
    env.process(move_ap(env, ap))
    env.process(clear_stats(env))
    logging.info("Mobility Setup done.")
