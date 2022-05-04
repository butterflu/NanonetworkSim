from base_classes import *



arguments = [8,]

print("not main")

rtr_packet = RTRPacket()
rtr_packet.set_parameters(1, 15, 1, 2, 1, 1, 5, 2, 1, 0, 12, 'payload')
print(rtr_packet)

data_packet = DATAPacket()
data_packet.set_parameters(0, 10, 2, 1, "data")
print(data_packet)

all_nodes = []
pl = PhyLink(rtr_packet.get_bytearray())
print((str(data_packet.get_bytearray())))

env = simpy.Environment()
n1 = Node(env, 1)
n2 = Node(env, 2)
n2.send_buffer.append(data_packet)

all_nodes.append(n1)
all_nodes.append(n2)
for x in range(3, 5):
    all_nodes.append(Node(env, x))

# for node in all_nodes:
#     env.process(queue_send(node, pl))

env.process(queue_send(all_nodes[0], pl))

print("start sim")
env.run(30)