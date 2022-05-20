from base_classes import *
from mobility import *
from functions import get_nodes_position

env = simpy.Environment()

#setup steps
setup_nodes(env)

print("start sim")
env.run(steps_in_s*sim_time_s)

print("sim end")
positions = get_nodes_position()
x = [x[0] for x in positions]
y = [y[1] for y in positions]

fig, ax = plt.subplots()
ax.scatter(x, y)
plt.show()