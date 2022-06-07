from base_classes import *
from mobility import *
from functions import get_nodes_position
from stats import *
import logging

env = simpy.Environment()
logging.basicConfig(level=logging.DEBUG, filename='logs.log', format='%(asctime)s %(levelname)s:%(message)s')


# setup steps
setup_nodes(env)

print("start sim")
env.run(steps_in_s * sim_time_s)

print("sim end")
positions = get_nodes_position()
x = [x[0] for x in positions]
y = [y[1] for y in positions]

fig, ax = plt.subplots()
ax.scatter(x, y)
# plt.show()

stats.print_stats()
stats.save_csv()
