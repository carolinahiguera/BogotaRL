'''
Created on oct 04, 2018

@author: carolina

INDEPENDENT Q LEARNING 
REVIEW: 04/10/2018

'''
import fun
import training
import testing
execfile("./fun.py")
execfile("./training.py")
execfile("./testing.py")
         
fun.learnDiscretization()
fun.writeDataClusters()
training.ind_QLearning()
testing.ind_QLearning()

print("end")