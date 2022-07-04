from numpy.random import uniform, binomial
import parameters as param
import numpy as np
from simpy import Environment
import logging
from functions import clear_stats

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


def setup_nodes(env):
    """
    function to set up nodes and assign them to propper lists
    :return:
    """
    if param.use_rih:
        from MAC_protocol.RIH import RTR_Node, RTR_AP, periodically_add_data
    elif param.use_ra:
        from MAC_protocol.RA import RA_AP, RA_Node, periodically_add_data
    elif param.use_2way:
        from MAC_protocol.TW import TW_AP, TW_Node, periodically_add_data
    else:
        print("no mode selected")
        exit(-1)

    print(f'nodes_num:{param.nodes_num}, ra:{param.use_ra}, rih:{param.use_rih},  2way:{param.use_2way}')
    logging.info('Starting node setup ...')

    # calucating several parameters to limit the simulation scope
    # calculating num of nodes using binomial distribution
    n = int(param.sim_time_s * param.velocity_mmps / 100 * np.pi * (
            (param.vein_diameter_mm / 200) ** 2) / param.blood_volume_l * param.nodes_num)
    num_simulated_nodes = binomial(n=2 * n, p=param.p)
    print(f'number of created node: {num_simulated_nodes}')

    x_start = -np.ceil((param.sim_time_s * param.velocity_mmps) + (param.startup_time / 2 * param.velocity_mmps))
    x_end = -param.startup_time / 2 * param.velocity_mmps

    # randomize positions, using polar coordinates to distribute uniformly

    r = np.multiply(param.vein_diameter_mm / 2, np.sqrt(uniform(size=num_simulated_nodes)))
    theta = uniform(0, 2 * np.pi, size=num_simulated_nodes)

    y_values = r * np.sin(theta)
    z_values = r * np.cos(theta) + (param.vein_diameter_mm / 2)

    x_uniform = uniform(x_start, x_end, size=num_simulated_nodes)
    x_values = [round(x, 3) for x in x_uniform]

    pos_combined = np.stack((x_values, y_values, z_values), axis=1)

    # add nano-router
    if param.use_rih:
        ap = RTR_AP(env=env, node_id=1)
    elif param.use_ra:
        ap = RA_AP(env=env, node_id=1)
    elif param.use_2way:
        ap = TW_AP(env=env, node_id=1)

    param.all_nodes.append(ap)
    param.simulated_nodes.append(ap)
    x1, y1, z1 = ap.get_pos()

    for node_id, pos in zip(range(2, num_simulated_nodes + 1), pos_combined):
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

    if param.use_rih is False:
        for node in param.relevant_nodes:
            node.setup_node_surrondings()
            if param.simulated_nodes.index(node) % 1000 == 0:
                print(f'node nr {param.simulated_nodes.index(node)} done')

    env.process(move_ap(env, ap))
    env.process(clear_stats(env))
    logging.info(f"Added {num_simulated_nodes} nodes")
    logging.info(f'number of simulated nodes: {len(param.simulated_nodes)}')
    logging.info("Node Setup done.")
