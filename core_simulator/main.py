from base_classes import *
from scipy import stats
env = simpy.Environment()

# nodes
ap = AP(env, 1)
all_nodes.append(ap)

for x in range(2, 5):
    all_nodes.append(Node(env, x))
    env.process(periodically_add_data(all_nodes[x - 1], 1))

print("start sim")
env.run(steps_in_s*sim_time_s)
