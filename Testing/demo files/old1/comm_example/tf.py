import os

FIFO_IN_0 = '/tmp/mypipe_in_0'
# FIFO_OUT_0 = '/tmp/mypipe_out_0'

while True:
    input() 
    print('Enviando datos')
    fifo_in_0 = open(FIFO_IN_0, 'w')
    fifo_in_0.write('hola')
    fifo_in_0.close()
    print('Esperando step')
    fifo_in_0 = open(FIFO_IN_0, 'r')
    line = fifo_in_0.read()
    fifo_in_0.close()
    print('Step recibido')