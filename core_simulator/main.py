from base_classes import *
from mobility import *
from functions import *
import logging
import time
import parameters as param

logging.basicConfig(level=logging.INFO, filename='logs.log', format='%(asctime)s %(levelname)s:%(message)s',
                    filemode='w')

fname = 'diameter'
# 100000, 200000, 500000, 800000, 1000000, 2000000, 3000000, 4000000
# (True, False, False), (False, True, False),  (False, False, True)
# [0.25, 0.5, 0.75, 1, 1.5, 3, 4, 5]
# setup steps
# prepare_csv(fname)
# TODO: check which 2 way is best
for nnodes in [2000000]:
    for vein_diameter_mm in [0.25, 0.5, 0.75, 1, 1.5, 3, 4, 5]:
        for i in range(30):
            param.nodes_num = nnodes
            param.use_2way = True
            param.vein_diameter_mm = vein_diameter_mm

            start_time = time.time()
            clear_sim()
            env = simpy.Environment()
            setup_nodes(env)

            print("start sim:" + str(i))
            env.run(param.steps_in_s * (param.sim_time_s + param.startup_time))
            print("sim end")
            logging.info("SIM END")
            if fname:
                append_csv(fname)
            else:
                append_csv()

            print("--- time of execution: %s seconds ---" % (time.time() - start_time))
