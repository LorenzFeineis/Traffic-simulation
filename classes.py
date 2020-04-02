import numpy as np
import random
import pprint
random.seed(40)


def prob_dist(num_points):
    dist = np.zeros((num_points,))
    for i in range(num_points):
        dist[i] = random.randint(1,10)
    dist = dist/sum(dist)
    return dist

class Street():
    def __init__(self,crossings, start, end, p_bummel = 0, capacity=100):
        self.start = crossings[start]
        self.end = crossings[end]
        self.cap = capacity
        self.edge = (self.start.index,self.end.index)
        self.p_bummel = p_bummel
        self.turning_lanes = []
        self.weights = True ### weights is a dictionary with keys, value pairs (inc,out) : weight
        cells = []
        for idx in range(capacity):
            cells.append(Cell(self,idx))
        self.cells = cells
        self.cars = []

    def random_weights(self):
        ### generates a discrete prob distribution of the lanes as a list
        self.weights = prob_dist(len(self.turning_lanes))

    def set_weights(self, weights):
        ### weights is a dictionary with keys, value pairs (inc,out) : weight
        turning_lanes = [lane.inc_out for lane in self.turning_lanes]
        try:
            if len(weights.keys())==len(turning_lanes) and sum(weights.values()) ==1:
                new_weights = [0 for lane in range(len(turning_lanes))]
                for lane in weights.keys():
                    new_weights[turning_lanes.index(lane)] = weights[lane]
                self.weights = new_weights
            else:
                print("weights for street {} is not suitable".format(self.edge))
        except TypeError:
            print("weights for street{} has to be the type of a list".format(self.edge))

    def distance_successors(self):
        try: ## The steet might be empty
            car = self.cars[0]
            direction = car.direction.out
            try:
                successor = direction.cars[-1].cell
                car.successor = successor
                car.distance = car.cell.idx + (direction.cap - 1 - car.successor.idx)
            except IndexError:
                car.distance = 100 ### no vehicle in important distance
                car.successor = None
            successor = car
        except IndexError:
            print("Street is empty")
        else:
            try:
                for car in self.cars[1:]:
                    car.successor = successor
                    car.distance = car.cell.idx - successor.cell.idx -1
                    successor = car
            except IndexError:
                print("Street has only one car")


class Cell():
    def __init__(self,street,idx = 0):
        self.street = street
        self.idx = idx
        self.state = None

class Car():
    def __init__(self, idx, length = 1, vmax = 2):
        self.idx = idx
        self.length = length
        self.vmax = vmax
        self.velocity = 0
        self.cell = None
        self.street = None
        self.direction = None ### Can be set to a turning lane of the current street
        self.successor = None
        self.distance = None ## The distance of cars front to back is 0
    def set_location(self, street, cell):
        self.street = street
        self.cell = cell
    def set_direction(self):
        street = self.street
        self.direction = random.choices(population = street.turning_lanes, weights = street.weights, k = 1)[0]

class Turning_lane():
    ### turning_lanes are generated for a crossing. A street has a turning lane
    ### for each outgoing edge from the crossing. If a turning is allowed on
    ### this turning lane is described by street.weights
    def __init__(self, incoming, outcoming, crossing, light = False):
        self.inc = incoming
        self.out = outcoming
        self.node = crossing
        self.light = light  ## Lights are set for turning lanes but should
                            ## actually be the same for each turning lane on the
                            ## same street.
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
        ### generates every possible turning lane at this cross.
        for inc in self.inc:
            for out in self.out:
                lane = Turning_lane(inc, out ,self)
                system.turning_lanes[(inc,out,self)] = lane
                self.turning_lanes[(inc,out,self)] = lane
                inc.turning_lanes.append(lane)
    def switch_lights(self, setting):
        ### setting is a list of the form [(incoming street, outgoing street), ...]
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
            street.random_weights()
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
        self.num_cars = [] ### contains [len(street.cars) for street in self.streets]
        self.moved_cars = []
        self.std_num_cars = []
        self.cars = []

    ### The following methods include the classes cells and cars for more
    ### realistic traffic simulationsreturn something
    def random_init_cars(self,cars, bottombound, upperbound):
        # cars is a list containing cars
        num_cars = []
        for street in self.edges:
            upperbound = min([upperbound,street.cap])
            for cell_id in range(random.randint(bottombound,upperbound)):
                # this removes the first car in cars and puts it at the cell
                car = cars.pop(0)
                street.cells[cell_id].state = car
                car.street = street
                car.cell = street.cells[cell_id]
                self.cars.append(car)
                street.cars.append(car)
                car.set_direction()
            num_cars.append(len(street.cars))
        self.num_cars.append(num_cars)
        self.std_num_cars.append(np.std(num_cars))

    def det_distance_successor(self):
        for street in self.edges:
            street.distance_successors()

    def accelerate_cars(self):
        for car in self.cars:
            car.velocity = min(car.velocity+1,car.vmax)

    def decelerate_cars(self):
        for car in self.cars:
            if car.distance < car.velocity:
                car.velocity = car.distance
            if car.direction.light == False:
                car.velocity = min(car.velocity, car.cell.idx)

    def bummeln(self):
        for street in self.edges:
            p_bummel = street.p_bummel
            for car in street.cars:
                if random.uniform(0,1)<p_bummel:
                    min(0, np.abs(car.velocity - 1))

    def move_cars(self):
        moved_cars = 0
        for car in self.cars:
            if car.velocity >0 :
                moved_cars+=1
                if car.cell.idx < car.velocity: ## car turns in new street
                    car.street.cars.remove(car)
                    new_street = car.direction.out
                    new_street.cars.append(car)
                    new_cell = new_street.cells[new_street.cap - car.velocity + car.cell.idx ]
                    car.street = car.direction.out
                    car.cell = new_cell
                    car.set_direction()
                else:
                    car.cell = car.street.cells[car.cell.idx - car.velocity]
        self.moved_cars.append(moved_cars)

    def time_step_cars(self):
        self.time +=1
        self.det_distance_successor()
        self.accelerate_cars()
        self.decelerate_cars()
        self.bummeln()
        self.move_cars()
        self.num_cars.append([len(street.cars) for street in self.edges])
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
