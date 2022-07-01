from base_classes import *
from mobility import *
from functions import *
import logging
import time
import parameters as param

logging.basicConfig(level=logging.INFO, filename='logs.log', format='%(asctime)s %(levelname)s:%(message)s',
                    filemode='w')

# setup steps
# prepare_csv()
for nnodes in [ 800000, 500000, 1000000, 2000000, 3000000, 4000000]:
    for rih, ra in [(True, False), (False, True)]:
        for i in range(5):
            param.nodes_num = nnodes
            param.use_ra = ra
            param.use_rih = rih
            start_time = time.time()
            clear_sim()
            env = simpy.Environment()
            setup_nodes(env)
            # show_yz_coords()

            print("start sim:" + str(i))
            env.run(param.steps_in_s * (param.sim_time_s + param.startup_time))
            print("sim end")
            append_csv()

            print("--- time of execution: %s seconds ---" % (time.time() - start_time))
