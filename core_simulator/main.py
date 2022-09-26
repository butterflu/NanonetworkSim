from base_classes import *
from mobility import *
from functions import *
import logging
import time
import parameters as param

logging.basicConfig(level=logging.INFO, filename='logs.log', format='%(asctime)s %(levelname)s:%(message)s',
                    filemode='w')

fname = 'test'
# 100000, 200000, 500000, 800000, 1000000, 2000000, 3000000, 4000000
# (True, False, False), (False, True, False),  (False, False, True)
# setup steps
prepare_csv(fname)
for nnodes in [ 100000 ]:
    for rih, ra, two_way in [(False, False, True)]:
        for i in range(30):
            param.nodes_num = nnodes
            param.use_ra = ra
            param.use_rih = rih
            param.use_2way = two_way


            start_time = time.time()
            clear_sim()
            env = simpy.Environment()
            setup_nodes(env)
            # show_yz_coords()

            print("start sim:" + str(i))
            env.run(param.steps_in_s * (param.sim_time_s + param.startup_time))
            print("sim end")
            logging.info("SIM END")
            append_csv(fname)

            print("--- time of execution: %s seconds ---" % (time.time() - start_time))
