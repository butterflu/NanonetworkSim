import random

import simpy


class node(object):

    all_nodes=[]

    def __init__(self, env):
        self.id=len(self.all_nodes)
        self.env = env
        self.data_to_send=[]         #id, size
        self.receive_buffer=0       #size
        self.receive_process = self.env.process(self.receive(10))
        self.all_nodes.append(self.receive_process)
        self.main_process = self.env.process(self.main())
        self.RTR_rec = False
        self.env.process(self.input_simulator())

    def main(self):
        while True:
            # print(self.id, '-Loop beginning:', self.env.now)
            # send RTR
            self.send_RTR()
            self.RTR_rec = False
            # receive data
            self.all_nodes[self.id] = self.env.process(self.receive(10))
            yield self.all_nodes[self.id] & self.env.timeout(random.randint(10, 14))

            # send data
            if self.data_to_send != [] and self.RTR_rec:
                self.send()

    def send(self, target=None,  is_RTR = False):
        msg='Data'
        # print("Sending:", target, is_RTR)
        if target is None:
            target, data = self.data_to_send.pop()
        target_process = self.all_nodes[target]
        if not target_process.triggered:
            if is_RTR:
                msg = 'RTR'
            else:
                print(self.id, "-Sending data to", target)
            target_process.interrupt(msg)
        else:
            # print("No receiver")
            pass
    def send_RTR(self):
        for node in [x for x in range(len(self.all_nodes)) if x != self.id]:
            self.send(node, True)

    def receive(self, time):
        try:
            yield self.env.timeout(time)
        except simpy.Interrupt as i:
            if i.cause == 'RTR':
                self.RTR_rec=True
            print(self.id, "-message recieved:", i.cause)

    def input_simulator(self):
        target = random.choice([x for x in range(len(self.all_nodes)) if x != self.id])
        while True:
            yield self.env.timeout(random.randint(10, 20))
            self.data_to_send.append([target, 10])



