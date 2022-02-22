import simpy


class Node:

    def __init__(self, env):
        self.receiver = simpy.Resource(env, capacity=1)


    def send(self,env, header, data):
        pass







if __name__ == "__main__":
    pass