import classes as tr
import numpy as np
import matplotlib.pyplot as plt


A = [[0,100,0,0,100,0],
    [100,0,100,100,0,0],
    [0,100,0,100,0,0],
    [0,100,100,0,100,100],
    [100,0,0,100,0,100],
    [0,0,100,100,0,0]]

A = 100*np.array(A)
system_2 = tr.build_system(A)
traf_2 = tr.Traffic(system_2)

### Possble traffic light settings###

## Crossing 0
cros0_1 = [(4,1),(1,4)]
cros0_2 = [(1,1),(4,4)]

## Crossing 1
cros1_1 = [(0,3),(0,2),(3,0)]
cros1_2 = [(2,0),(2,3),(0,2)]

## Crossing 2
cros2_1 = [(3,1),(1,3)]
cros2_2 = [(5,3),(5,1)]
cros2_3 = [(5,3),(3,1)]

## Crossing 3
cros3_1 = [(5,1),(5,4),(1,5),(1,2)]
cros3_2 = [(2,4),(2,5),(4,2),(4,1)]
cros3_3 = [(5,2),(1,4)]
cros3_4 = [(2,1),(4,5)]

## Crossing 4
cros4_1 = [(0,5),(0,3)]
cros4_2 = [(0,3),(3,0)]
cros4_3 = [(3,5),(3,0)]

## Crossing 5
cros5_1 = [(4,2),(4,3)]
cros5_2 = [(3,2),(4,3)]

### Setting the weights

##Street (0,1)
traf_2.system.streets[(0,1)].set_weights({(0,0):0, (0,2):0.45,(0,3):0.55})
traf_2.system.streets[(0,4)].set_weights({(0,0):0,(0,3):0.65,(0,5):0.35})
traf_2.system.streets[(1,0)].set_weights({(1,1):0.1,(1,4):0.9})
traf_2.system.streets[(1,2)].set_weights({(1,1):0,(1,3):1})
traf_2.system.streets[(1,3)].set_weights({(1,1):0,(1,2):0.4,(1,5):0.3,(1,4):0.3})
traf_2.system.streets[(2,1)].set_weights({(2,2):0,(2,3):0.5,(2,0):0.5})
traf_2.system.streets[(2,3)].set_weights({(2,2):0,(2,1):0,(2,4):0.5,(2,5):0.5})
traf_2.system.streets[(3,1)].set_weights({(3,3):0,(3,0):0.5,(3,2):0.5})
traf_2.system.streets[(3,2)].set_weights({(3,3):0,(3,1):1})
traf_2.system.streets[(3,4)].set_weights({(3,3):0,(3,0):0.5,(3,5):0.5})
traf_2.system.streets[(3,5)].set_weights({(3,3):0,(3,2):1})
traf_2.system.streets[(4,0)].set_weights({(4,4):0.1,(4,1):0.9})
traf_2.system.streets[(4,3)].set_weights({(4,4):0,(4,1):0.5,(4,2):0.5,(4,5):0})
traf_2.system.streets[(4,5)].set_weights({(4,3):0.2,(4,2):0.8})
traf_2.system.streets[(5,2)].set_weights({(5,1):0.7,(5,3):0.3})
traf_2.system.streets[(5,3)].set_weights({(5,5):0,(5,1):0.8,(5,2):0.05,(5,4):0.15})
############## Testing #################

traf_2.random_init(20,60)


print(traf_2.num_cars[-1])
for time in range(1000):
    print(time)
    if time%5 ==0 and time%3==1:
        traf_2.nodes[0].swicht_lights(cros0_1)
        traf_2.nodes[1].swicht_lights(cros1_1)
        traf_2.nodes[2].swicht_lights(cros2_1)
        traf_2.nodes[3].swicht_lights(cros3_1)
        traf_2.nodes[4].swicht_lights(cros4_1)
        traf_2.nodes[5].swicht_lights(cros5_1)
    if time%5==0 and time%3==0:
        traf_2.nodes[0].swicht_lights(cros0_2)
        traf_2.nodes[1].swicht_lights(cros1_2)
        traf_2.nodes[2].swicht_lights(cros2_2)
        traf_2.nodes[3].swicht_lights(cros3_2)
        traf_2.nodes[4].swicht_lights(cros4_2)
        traf_2.nodes[5].swicht_lights(cros5_2)
    if time%5==0 and time%3==2:
        traf_2.nodes[2].swicht_lights(cros2_3)
        traf_2.nodes[3].swicht_lights(cros3_3)
        traf_2.nodes[4].swicht_lights(cros4_3)
    traf_2.time_step()
    print(traf_2.num_cars[-1])
    print("moved_cars:",traf_2.moved_cars[-1])


print(traf_2.std_num_cars)
