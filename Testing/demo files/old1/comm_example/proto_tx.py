import os
import sys
sys.path.insert(0,'../')
from proto.sumo_data_pb2 import SumoData

FIFO = '/tmp/sumo_tf'

data = SumoData()
data.time_stamp = 10
for i in range(6):
	action = data.action.add()
	action.id = i
	action.action = tu_accion


for i in range(10):
	data.edge_names.extend([f'hola {i}'])
	data.speeds.extend([10.0*i])
print(data)

os.mkfifo(FIFO)

print('Escribiendo datos')

fifo = open(FIFO, 'wb')
fifo.write(data.SerializeToString())
fifo.close()

print('Finalizado')
