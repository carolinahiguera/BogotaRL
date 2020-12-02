'''
Created on 26/09/2016

@author: carolina
@summary: variable elimination algorithm following description of Kok and Vlassis (payoff propagation)
'''

import numpy as np
import random
import var
import itertools

def Algorithm():
    
    #Eliminar agente 0
    jAct = list(itertools.product(var.vertexAgents[0].actionPhases, var.vertexAgents[3].actionPhases, var.vertexAgents[1].actionPhases))
    g={}
    for i in range(len(jAct)):
        a0 = jAct[i][0]
        a3 = jAct[i][1]
        a1 = jAct[i][2]
        g[jAct[i]] = var.edgeAgents[1].getQValue(a0,a3) + var.edgeAgents[0].getQValue(a0,a1)
    act = list(itertools.product(var.vertexAgents[3].actionPhases, var.vertexAgents[1].actionPhases))
    phi_31 = {}
    for i in range(len(act)):
        phi_31[act[i]] = (max(g[(0,)+act[i]], g[(2,)+act[i]]))
    
    #Eliminar agente 3
    jAct = list(itertools.product(var.vertexAgents[3].actionPhases, var.vertexAgents[4].actionPhases, var.vertexAgents[1].actionPhases))
    g={}
    for i in range(len(jAct)):
        a3 = jAct[i][0]
        a4 = jAct[i][1]
        a1 = jAct[i][2]
        g[jAct[i]] = var.edgeAgents[5].getQValue(a3,a4) + phi_31[(a3,a1)]
    act = list(itertools.product(var.vertexAgents[4].actionPhases, var.vertexAgents[1].actionPhases))
    phi_41 = {}
    for i in range(len(act)):
        phi_41[act[i]] = (max(g[(0,)+act[i]], g[(2,)+act[i]]))
        
    #Eliminar agente 4
    jAct = list(itertools.product(var.vertexAgents[4].actionPhases, var.vertexAgents[1].actionPhases, var.vertexAgents[5].actionPhases))
    g={}
    for i in range(len(jAct)):
        a4 = jAct[i][0]
        a1 = jAct[i][1]
        a5 = jAct[i][2]
        g[jAct[i]] = var.edgeAgents[3].getQValue(a1,a4) + var.edgeAgents[6].getQValue(a4,a5)  + phi_41[(a4,a1)]
    act = list(itertools.product(var.vertexAgents[1].actionPhases, var.vertexAgents[5].actionPhases))
    phi_15 = {}
    for i in range(len(act)):
        phi_15[act[i]] = (max(g[(0,)+act[i]], g[(2,)+act[i]]))
    
    #Eliminar agente 1
    jAct = list(itertools.product(var.vertexAgents[1].actionPhases, var.vertexAgents[2].actionPhases, var.vertexAgents[5].actionPhases))
    g={}
    for i in range(len(jAct)):
        a1 = jAct[i][0]
        a2 = jAct[i][1]
        a5 = jAct[i][2]
        g[jAct[i]] = var.edgeAgents[2].getQValue(a1,a2) + phi_15[(a1,a5)]
    act = list(itertools.product(var.vertexAgents[2].actionPhases, var.vertexAgents[5].actionPhases))
    phi_25 = {}
    for i in range(len(act)):
        phi_25[act[i]] = (max(g[(0,)+act[i]], g[(2,)+act[i]]))
    
    #Eliminar agente 2
    jAct = list(itertools.product(var.vertexAgents[2].actionPhases, var.vertexAgents[5].actionPhases))
    g={}
    for i in range(len(jAct)):
        a2 = jAct[i][0]
        a5 = jAct[i][1]
        g[jAct[i]] = var.edgeAgents[4].getQValue(a2,a5) + phi_25[(a2,a5)]
    act = list(itertools.product(var.vertexAgents[5].actionPhases))
    phi_5 = {}
    for i in range(len(act)):
        phi_5[act[i]] = (max(g[(0,)+act[i]], g[(2,)+act[i]]))
        
    #Mejor accion para el agente 5
    best = -np.inf
    a5 = -1
    for a in  var.vertexAgents[5].actionPhases:
        if(best < phi_5[(a,)]):
            best = phi_5[(a,)]
            a5 = a
        elif(best == phi_5[(a,)]):
            if(random.random() < 0.5):
                a5 = a
    
    #Mejor accion para el agente 2
    best = -np.inf
    a2 = -1
    for a in  var.vertexAgents[2].actionPhases:
        if(best < (var.edgeAgents[4].getQValue(a,a5) + phi_25[(a,a5)])):
            best = var.edgeAgents[4].getQValue(a,a5) + phi_25[(a,a5)]
            a2 = a
        elif(best == (var.edgeAgents[4].getQValue(a,a5) + phi_25[(a,a5)])):
            if(random.random() < 0.5):
                a2 = a
    
    #Mejor accion para el agente 1
    best = -np.inf
    a1 = -1
    for a in  var.vertexAgents[1].actionPhases:
        if(best < (var.edgeAgents[2].getQValue(a,a2) + phi_15[(a,a5)])):
            best = var.edgeAgents[2].getQValue(a,a2) + phi_15[(a,a5)]
            a1 = a
        elif(best == (var.edgeAgents[2].getQValue(a,a2) + phi_15[(a,a5)])):
            if(random.random() < 0.5):
                a1 = a
        
    
    #Mejor accion para el agente 4
    best = -np.inf
    a4 = -1
    for a in  var.vertexAgents[4].actionPhases:
        if(best < (var.edgeAgents[3].getQValue(a1,a) + var.edgeAgents[6].getQValue(a,a5) + phi_41[(a,a1)])):
            best = var.edgeAgents[3].getQValue(a1,a) + var.edgeAgents[6].getQValue(a,a5) + phi_41[(a,a1)]
            a4 = a
        elif(best == (var.edgeAgents[3].getQValue(a1,a) + var.edgeAgents[6].getQValue(a,a5) + phi_41[(a,a1)])):
            if(random.random() < 0.5):
                a4 = a
    
    #Mejor accion para el agente 3
    best = -np.inf
    a3 = -1
    for a in  var.vertexAgents[3].actionPhases:
        if(best < (var.edgeAgents[5].getQValue(a,a4) + phi_31[(a,a1)])):
            best = var.edgeAgents[5].getQValue(a,a4) + phi_31[(a,a1)]
            a3 = a
        elif(best == (var.edgeAgents[5].getQValue(a,a4) + phi_31[(a,a1)])):
            if(random.random() < 0.5):
                a3 = a
            
    #Mejor accion para el agente 0
    best = -np.inf
    a0 = -1
    for a in  var.vertexAgents[0].actionPhases:
        if(best < (var.edgeAgents[2].getQValue(a,a3) + var.edgeAgents[1].getQValue(a,a1))):
            best = var.edgeAgents[2].getQValue(a,a3) + var.edgeAgents[1].getQValue(a,a1)
            a0 = a
        elif(best == (var.edgeAgents[2].getQValue(a,a3) + var.edgeAgents[1].getQValue(a,a1))):
            if(random.random() < 0.5):
                a0 = a
    
    var.bestJointAction = [a0, a1, a2, a3, a4, a5]
    

