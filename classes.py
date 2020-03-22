import numpy as np
import random
import pprint
random.seed(42)


def prob_dist(num_points):
    dist = np.zeros((num_points,))
    for i in range(num_points):
        dist[i] = random.randint(1,10)
    dist = dist/sum(dist)
    return dist

class Street():
    def __init__(self,crossings, start, end, num_cars = 0, capacity=10000):
        self.start = crossings[start]
        self.end = crossings[end]
        self.cap = capacity
        self.edge = (self.start.index,self.end.index)
        self.num_cars = num_cars
        self.turning_lanes = []
        self.weights = True
    def distribute_on_lanes(self):
        ### generates a discrete prob distribution of the lanes as a list
        self.weights = prob_dist(len(self.turning_lanes))
    def set_weights(self, weights):
        ### weights is a dictionary with keys, value pairs (inc,out) : weight
        turning_lanes = [lane.inc_out for lane in self.turning_lanes]
        try:
            if len(weights.keys())==len(turning_lanes) and sum(weights.values()) ==1:
                new_weights = [0 for lane in range(len(turning_lanes))]
                for lane in weights:
                    new_weights[turning_lanes.index(lane)] = weights[lane]
                self.weights = new_weights
            else:
                print("weights for street {} is not suitable".format(self.edge))
        except TypeError:
            print("weights for street{} has to be the type of a list".format(self.edge))


class turning_lane():
    def __init__(self, incoming, outcoming, crossing, light = False):
        self.inc = incoming
        self.out = outcoming
        self.node = crossing
        self.light = light
        self.num_cars = 0
        self.inc_out = (self.inc.edge[0],self.out.edge[1])
    def green(self):
        self.light = True
    def red(self):
        self.light = False
    def parameter(self):
        return (self.inc, self.out, self.node, self.light)

class Crossing():
    def __init__(self, index):
        self.index = index
        self.inc = []
        self.out = []
        self.turning_lanes = {}
    def incoming(self, system):
        inc = []
        for idx, capacity in enumerate(system.capacities()[:,self.index]):
            if capacity > 0:
                try:
                    inc.append(system.streets[(idx,self.index)])
                except KeyError:
                    continue
        self.inc = inc
    def outgoing(self, system):
        out = []
        for idx, capacity in enumerate(system.capacities()[self.index,:]):
            if capacity > 0:
                try:
                    out.append(system.streets[(self.index,idx)])
                except KeyError:
                    continue
        self.out = out
    def generate_turning_lanes(self, system):
        for inc in self.inc:
            for out in self.out:
                lane = turning_lane(inc, out ,self)
                system.turning_lanes[(inc,out,self)] = lane
                self.turning_lanes[(inc,out,self)] = lane
                inc.turning_lanes.append(lane)
    def swicht_lights(self, setting):
        try:
            for lane in self.turning_lanes.keys():
                if (lane[0].edge[0],lane[1].edge[1]) in setting:
                    self.turning_lanes[lane].green()
                else:
                    self.turning_lanes[lane].red()
        except KeyError:
            print("Setting {} is not suitable".format(setting))

class System():
    def __init__(self, crossings=[], streets=[]):
        self.nodes = crossings
        self.edges = streets
        self.streets = {street.edge:street for street in streets}
        ### the following is generated in the Crossing method set_turning_lanes
        self.turning_lanes = {} ### keys: (inc,out,cros) values: turning_lane
        for crossing in crossings:
            crossing.incoming(self)
            crossing.outgoing(self)
            crossing.generate_turning_lanes(self)
        for street in streets:
            street.distribute_on_lanes()
    def capacities(self):
        n = len(self.nodes)
        A = np.zeros((n,n))
        for street in self.edges:
            A[street.start.index,street.end.index] = street.cap
        return A
    def crossing_at(idx):
        return self.nodes[idx]



class Traffic():
    ### Traffic heirs some properties from System
    def __init__(self, system, time =0):
        self.system = system
        self.nodes = system.nodes
        self.edges = system.edges
        self.turning_lanes = system.turning_lanes
        self.time = time
        self.num_cars = []
        self.moved_cars = []
        self.std_num_cars = []
    def random_init(self,bottombound=0,upperbound =100):
        appendix = []
        for street in self.edges:
            upperbound = min([upperbound,street.cap])
            street.num_cars = random.randrange(bottombound,upperbound)
            appendix.append(street.num_cars)
        self.num_cars.append(appendix)
        self.std_num_cars.append(np.std(appendix))
    def distribute_cars(self):
        ### distributes all new cars in a lane onto the available turning_lanes
        for street in self.edges:
            old_cars = sum([lane.num_cars for lane in street.turning_lanes])
            new_cars = street.num_cars - old_cars
            turning_lanes = random.choices(population = street.turning_lanes, weights = street.weights, k = new_cars)
            for turning_lane in turning_lanes:
                turning_lane.num_cars +=1
    def time_step(self):
        self.time +=1
        changes = []
        for street in self.edges:
            for turning_lane in street.turning_lanes:
                if turning_lane.light and turning_lane.num_cars >0:
                    if turning_lane.out.num_cars < turning_lane.out.cap:
                        changes.append(turning_lane)
        for turning_lane in changes:
            turning_lane.num_cars -=1
            turning_lane.inc.num_cars -=1
            turning_lane.out.num_cars +=1
        self.moved_cars.append(len(changes))
        self.distribute_cars()
        self.num_cars.append([street.num_cars for street in self.edges])
        self.std_num_cars.append(np.std(self.num_cars[-1]))

def build_system(adjadency):
    ### Creates a system from a given adjadency matrix
    adjadency = np.array(adjadency)
    crossing = [Crossing(idx) for idx in range(adjadency.shape[0])]
    streets = [Street(crossing, indices[0], indices[1], capacity = adjadency[indices[0],indices[1]] ) for indices in np.argwhere(adjadency>0).tolist()]
    return System(crossing, streets)

############################################################
############################################################
################---Testing-Area---##########################
############################################################
############################################################
