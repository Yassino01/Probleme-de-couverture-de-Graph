#!/usr/bin/python3
from pars import graph_fromFile
from display import drawGraph
from collections import deque
from graph import rndm
from graph import algo_matching
from graph import algo_greedy
import time
import numpy as np
import matplotlib.pyplot as plt
import math

def stat_rndm(nmax,p,inst,inter):
    stat=np.zeros(shape=(inter,inst))
    for i in range(1,inter+1):
        for j in range(1,inst+1):
            start_time = time.time()
            g=rndm(int(i*nmax/(inter+1)),p)
            end_time = time.time()
            stat[i-1,j-1]= end_time -start_time
    return np.mean(stat,axis=1)

def display_time_matching_vs_greedy(nmax,p,inst,inter):  
    stat=np.zeros(shape=(inter,inst))
    stat2=np.zeros(shape=(inter,inst))
    for i in range(1,inter+1):
        for j in range(1,inst+1):
            g=rndm(int(i*nmax/(inter+1)),p)
            start_time = time.time()
            algo_matching(g)
            end_time = time.time()
            start_time2 = time.time()
            algo_greedy(g)
            end_time2 = time.time()
            stat[i-1,j-1]= end_time -start_time
            stat2[i-1,j-1]= end_time2 -start_time2
    stat,stat2=np.mean(stat,axis=1),np.mean(stat2,axis=1)   
    plt.plot([int(i*nmax/(inter+1)) for i in range(1,inter+1)],list(stat),label='Algorithme de couplage')
    plt.plot([int(i*nmax/(inter+1)) for i in range(1,inter+1)],list(stat2),label='Algorithme glouton')
    plt.legend()
    #plt.yscale("log")
    plt.ylabel('Moyenne de temps d\'exécution (s)')
    plt.xlabel('Taille des instances de Graph (nb de sommets)')
    plt.show()
    
def display_size_matching_vs_greedy(nmax,p,inst,inter):
    plt.figure()
    ax = plt.subplot(111)
    width=5
    stat=np.zeros(shape=(inter,inst))
    stat2=np.zeros(shape=(inter,inst))
    for i in range(1,inter+1):
        for j in range(1,inst+1):
            g=rndm(int(i*nmax/(inter+1)),p)
            m=len(algo_matching(g))
            n=len(algo_greedy(g))
            stat[i-1,j-1]= m
            stat2[i-1,j-1]= n
    stat,stat2=np.mean(stat,axis=1),np.mean(stat2,axis=1) 
    ax.bar([int(i*nmax/(inter+1))+width for i in range(1,inter+1)],list(stat),width,color='r',label='Algo glouton')
    ax.bar([int(i*nmax/(inter+1)) for i in range(1,inter+1)],list(stat2),width,color='g',label='Algo couplage')
    plt.legend()
    plt.ylabel('Taille de la couverture renvoyée')
    plt.xlabel('Taille des instances de Graph (nb de sommets)')
    plt.show()

def find_couv(g,c_opt,c_curent):
    e=g.first_edge()
    if e is not None:
        i,j=e
        gi=g.copy()
        gi.delete_node(i)
        gj=g.copy()
        gj.delete_node(j)
        c_i=c_curent.copy()
        c_i.add(i)
        c_j=c_curent.copy()
        c_j.add(j)
        find_couv(gi,c_opt,c_i)
        find_couv(gj,c_opt,c_j)
    else:
        if len(c_curent) < len(c_opt):
            c_opt.clear()
            c_opt.update(c_curent)

def branch_covering(g):
    c_opt=set(g._nodes)
    c_curent=set()
    find_couv(g,c_opt,c_curent)
    return c_opt
        
def iterative_branch_covering(g):
    c_opt=np.linspace(0,1,len(g._out)+1)
    stack = deque([g]) 
    if g is None:
        return
    while stack: 
        gcurrent = stack.pop() 
        e=gcurrent.first_edge() 
        if e is None:
            if (len(gcurrent._visites) < len(c_opt)):
                c_opt=set(gcurrent._visites)
        else:
            i,j=e
            gi,gj=gcurrent.copy(),gcurrent.copy()
            gi.delete_node(i)
            gj.delete_node(j)
            gi._visites.append(i)
            gj._visites.append(j)
            stack.extend([gj,gi])
    return c_opt
    

def iterative_branch_and_bound(g):
    global minactuel
    c_opt=np.linspace(0,1,len(g._out)+1)
    stack = deque([g]) 
    if g is None:
        return
    while stack:         
        gcurrent = stack.pop() 
        #print("graphe actuel:")
        #print(gcurrent._out)
        e=gcurrent.first_edge() 
        solrea=algo_greedy(gcurrent)+gcurrent._visites
        #print("minactuel: "+str(minactuel))
        #print("SOLREA --------")
        #print(solrea)
        bornesup=len(solrea)
        borneinf=g.graph_lower_bound()
        #print("Borne inf:")
        #print(borneinf)
        if (borneinf>=minactuel):
            #print(borneinf)
            #print(minactuel)
            continue
        #if (bornesup>minactuel):
        #    continue
        if (bornesup<len(c_opt)):
            c_opt=set(solrea)
            minactuel=bornesup
        if (bornesup<borneinf):
            c_opt=set(solrea)
            minactuel=bornesup
        #print("Borne inf: "+str(borneinf))
        if e is None:
            if (len(gcurrent._visites) < len(c_opt)):
                c_opt=set(gcurrent._visites)
            if (borneinf<minactuel):
                minactuel=borneinf
        else:
            i,j=e
            #print("(i,j): "+str((i,j)))
            gi,gj=gcurrent.copy(),gcurrent.copy()
            gi.delete_node(i)
            gj.delete_node(j)
            gi._visites.append(i)
            gj._visites.append(j)
            binfi=gi.graph_lower_bound()
            binfj=gj.graph_lower_bound()
            #print("binfi, binfj: "+str(binfi)+" "+str(binfj))
            #print(gi._out)
            #print(gj._out)
            if (binfi<binfj):
                stack.extend([gj,gi])
            else:
                stack.extend([gi,gj])
    return c_opt    
    
def display_branch_time(nmax,p,inst,inter):
    stat=np.zeros(shape=(inter,inst))
    stat2=np.zeros(shape=(inter,inst))
    for i in range(1,inter+1):
        for j in range(1,inst+1):
            g=rndm(int(i*nmax/(inter+1)),p)
            start_time = time.time()
            branch_covering(g)
            end_time = time.time()
            start_time2 = time.time()
            iterative_branch_and_bound(g)
            end_time2 = time.time()
            stat[i-1,j-1]= end_time -start_time
            stat2[i-1,j-1]= end_time2 -start_time2
    stat=np.mean(stat,axis=1)
    stat2=np.mean(stat2,axis=1)
    plt.plot([int(i*nmax/(inter+1)) for i in range(1,inter+1)],list(stat),label='Branchement récursif')
    plt.plot([int(i*nmax/(inter+1)) for i in range(1,inter+1)],list(stat2),label='Branchement itératif branch and bound')
    plt.legend()
    #plt.yscale("log")
    plt.ylabel('Moyenne de temps d\'exécution (s)')
    plt.xlabel('Taille des instances de Graph (nb de sommets)')
    plt.title("Durée d'exécution de l'algorithme de branchement")
    plt.show()
    
def display_branch_and_bound(nmax,p,inst,inter):
    stat=np.zeros(shape=(inter,inst))
   
    for i in range(1,inter+1):
        for j in range(1,inst+1):
            g=rndm(int(i*nmax/(inter+1)),p)
            start_time = time.time()
            iterative_branch_and_bound(g)
            end_time = time.time()
            stat[i-1,j-1]= end_time -start_time
    stat=np.mean(stat,axis=1)
    plt.plot([int(i*nmax/(inter+1)) for i in range(1,inter+1)],list(stat),label='Branchement itératif branch and bound')
    plt.legend()
    #plt.yscale("log")
    plt.ylabel('Moyenne de temps d\'exécution (s)')
    plt.xlabel('Taille des instances de Graph (nb de sommets)')
    plt.title("Durée d'exécution de l'algorithme de branchement")
    plt.show()    
    
if __name__ == "__main__":
  #g=Graph()
  inter=10 #nombre de taille differentes d'instance
  nmax=150 # taille max d'une instance
  inst=10 #nombre d'instance d'une taille donnée
  p=0.5 # parametre de construction d'un graph aléatoire
  g=graph_fromFile("file.txt")
  g=rndm(22,0.5)
  print(len(g))
  '''
  g.add_edge(1,2,-3)
  g.add_edge(1,4,-1)
  g.add_edge(2,3)
  print("nodes :")
  for e in g: 
    print(e)
  
  '''
  
  print(g._nodes)
  print(g._out)
  print(g._weight)
  print("degree :")
  a=g.degree()
  print(a)
  print(g.node_degMax())
  '''
  g.delete_node(1)

  print(g._nodes)
  print(g._out)
  print(g._weight)
  print("degree :")
  a=g.degree_max()
  print(a[0],a[1])

  '''
  g1=g.copy()
  
  
  #drawGraph(g1)

  g1.delete_nodes(['3','4'])
  print("G1:--------")
  print(g1._nodes)
  print(g1._out)
  print(g1._weight)
  print("degree :")
  a=g1.degree()
  print(a)

  
  """print("Couplage naif")
  print(algo_matching(g1))
  
  print("Couplage glouton")
  print(algo_greedy(g1))
  
  print("Branchement récursif")
  print(branch_covering(g1))
  """
  print("Branchement itératif")
  start=time.time()
  a=iterative_branch_covering(g)
  end=time.time()
  print(str(a)+" Taille de la solution: "+str(len(a))+" tps: "+str(end-start))
  
  print("Branch and bound itératif")
  minactuel=np.Infinity
  start=time.time()
  b=iterative_branch_and_bound(g)
  end=time.time()
  print(str(b)+" Taille de la solution: "+str(len(b))+" tps: "+str(end-start))
  
  #print(g.edge_number())
  
  #drawGraph(g1)
  #display_time_matching_vs_greedy(200,p,inst,inter)
  #display_size_matching_vs_greedy(nmax,p,inst,inter)
  n=18
  #display_branch_time(n,1/np.sqrt(n),inst,inter)
  n2=450
  #display_branch_and_bound(n2,1/np.sqrt(n2),inst,inter)
