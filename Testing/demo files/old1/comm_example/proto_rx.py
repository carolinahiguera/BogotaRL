import os
import sys
sys.path.insert(0,'../')
from proto.sumo_data_pb2 import SumoData

FIFO = '/tmp/sumo_tf'
data = SumoData()

while  True:
	print('Leyendo datos')
	fifo = open(FIFO, 'rb')
	data.ParseFromString(fifo.read())
	fifo.close()
	print('Finalizado')
	print(data)

