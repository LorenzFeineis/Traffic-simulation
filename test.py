import classes as tr
import numpy as np
### Definig the parameters
cros = []
for idx in range(5):
    cros.append(tr.Crossing(idx))

streets = [tr.Street(cros,0,4),tr.Street(cros,1,2),tr.Street(cros,2,4),tr.Street(cros,3,0),tr.Street(cros,4,1),tr.Street(cros,4,3)]

### Initializing the Trafficsystem
sys = tr.System(cros,streets)
traf = tr.Traffic(sys)
traf.random_init(30)
traf.distribute_cars()

### Turning all lights green
for street in traf.edges:
    for turning_lane in street.turning_lanes:
        turning_lane.green()
        #print(turning_lane.light)
