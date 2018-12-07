'''
Created on Jan 27, 2018

@author: carolina
'''

import numpy as np
import random
import var
import itertools

def getJointAct():
    elim_order = np.array(['tls_7_53', 'tls_9_53', 'tls_7_49', 'tls_7_47', 'tls_7_46',
                           'tls_7_45', 'tls_14_53', ''])
    joint_act = {}
    g={}
    tls_neighbors = {}
    graph = np.zeros( ( len(elim_order), len(elim_order) ) )
    for x in range(0, len(elim_order)):
        for y in  range(0, len(elim_order)):           
            if(elim_order[y] in var.agent_TLS[elim_order[x]].neighbors):
                graph[x,y] = 1
    
    phi = {}   
                
    #eliminar agentes del grafo
    for x in range(0,len(elim_order)-1):
        tls = elim_order[x]               
        nb_Q = elim_order[np.logical_or(graph[x,]==1, graph[x,]==3)]
        nb_phi = elim_order[np.logical_or(graph[x,]==2, graph[x,]==3)]
        neighbors = list(nb_phi)+list(nb_Q)
        
        if(list(nb_phi) != []):
            if(nb_phi[0] in nb_Q):
                idx = np.where(nb_Q == nb_phi[0])[0][0]
                aux_Q = np.delete(nb_Q, idx)
                neighbors = list(nb_phi)+list(aux_Q)
        
        tls_neighbors[tls] = neighbors
        
        list_actions = [var.agent_TLS[tls].actionPhases]
        for nb in neighbors:
            list_actions.append(var.agent_TLS[nb].actionPhases)
        jAct = []
        #acciones conjuntas entre agentes vecinos
        for i in itertools.product(*list_actions):
            jAct.append(i)
            
        #get QValues
        g[tls]={}
        for pair in jAct:
            g[tls][pair] = 0
            for nb in range(0,len(neighbors)):
                ai = pair[0]
                aj = pair[nb+1]                 
                if(neighbors[nb] in nb_Q):      
                    edge = (tls,neighbors[nb])
                    if(edge not in var.edges):
                        edge = (neighbors[nb],tls)      
                    g[tls][pair] += var.agent_Edge[edge].getQValue(ai, aj)
                if(neighbors[nb] in nb_phi):
                    edge = [(n1,n2) for n1, n2 in phi.keys() if n1==tls][0]
                    #edge = [item for item in phi.keys() if tls in item][0]
                    if((ai,aj) in phi[edge].keys()):       
                        g[tls][pair] += phi[edge][(ai,aj)]
                    else:
                        print("error calculando phi en VE")
                    
        #get joint actions of neighbors
        if(neighbors[0] == elim_order[-1]):
            edge = (neighbors[0],)
        else:
            edge = (neighbors[0],neighbors[1])        
            nb_i = np.where(elim_order==neighbors[0])[0][0]
            nb_j = np.where(elim_order==neighbors[1])[0][0]
            if(graph[nb_i, nb_j] == 1):
                graph[nb_i, nb_j] = 3
            else:
                graph[nb_i, nb_j] = 2
            if(graph[nb_j, nb_i] == 1):
                graph[nb_j, nb_i] = 3
            else:
                graph[nb_j, nb_i] = 2
            
        phi[edge]={}
            
        del list_actions[0]
        jAct = []       
        for i in itertools.product(*list_actions):
            jAct.append(i)
        for i in range(0,len(jAct)):
            u=[]
            for a in var.agent_TLS[tls].actionPhases:
                pair = (a,)+jAct[i]
                u.append(g[tls][pair])
            phi[edge][jAct[i]] = max(u)
        graph[x,:]= -1
        graph[:,x]= -1
    #Fin eliminacion
    
    #Calculo de accion conjunta
    for  x in range(len(elim_order)-1, -1, -1):
        tls = elim_order[x]
        if(tls == elim_order[-1]):
            pairs = [key for key,val in phi[(tls,)].iteritems() if val == max(phi[(tls,)].values())]
            idx = random.randint(0,len(pairs)-1)
            joint_act[tls] = pairs[idx][0]
        else:
            neighbors = tls_neighbors[tls]
            list_actions = [var.agent_TLS[tls].actionPhases]
            for nb in neighbors:
                list_actions.append([joint_act[nb]])
            jAct = []
            for i in itertools.product(*list_actions):
                jAct.append(i)
            g_filter = dict((k,v) for k,v in g[tls].iteritems() if k in jAct)
            pairs = [key for key,val in g_filter.iteritems() if val == max(g_filter.values())]
            idx = random.randint(0,len(pairs)-1)
            joint_act[tls] = pairs[idx][0]
    
    #print("fin VE")
    return joint_act
        
                
                
            
        
        
