import os
import pandas as pd

FIFO_IN_0 = '/tmp/sumo_tf'

print('Creando tuberías')
os.mkfifo(FIFO_IN_0)
print('Tuberías creadas')

while True:
    print('Esperando datos de simulación')
    fifo_in_0 = open(FIFO_IN_0, 'r')
    pd1 = pd.read_csv(fifo_in_0)
    print(pd1) 
    fifo_in_0.close()
    print('Datos recibidos')
    input()
    print('Enviando step')
    fifo_in_0 = open(FIFO_IN_0, 'w')
    fifo_in_0.write('chao')
    fifo_in_0.close()
    print('Step enviado')

