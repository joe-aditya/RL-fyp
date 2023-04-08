
ContainerNumber = 6
NodeNumber = 4
ServiceNumber = 4
ResourceType = 2
service_containernum = [1,1,3,1]
service_container = [[0],[1],[2,3,4],[5]] 
service_container_relationship = [0,1,2,2,2,3]
alpha = 0.5 # reward weighting factor
beta =[0.5,0.5]
count = 0
CPUnum = 4
Mem = 4*1024

import numpy as np
import agent 
from deploy import deploy
from mappings import getContainerDetails,getNodeName
from metrics import getCpuUsagePercentage, getMemoryUsagePercentage

class Env():
    def __init__(self):
        self.State = []
        self.node_state_queue = []
        self.container_state_queue = []
        self.action_queue = []
        self.prepare()

    def prepare(self):
        self.container_state_queue = [-1,-1,-1,-1,-1,-1]

        for i in range(NodeNumber):
            self.node_state_queue.extend( [ 0,0,0,0,0,0, 0 , 0 ] )
        self.State = self.container_state_queue + self.node_state_queue
        self.action = [-1,-1]
        self.action_queue = [-1,-1]
        # Communication weight between microservices
        self.service_weight = [[0,1,0,0],[1,0,1,0],[0,1,0,2],[0,0,2,0]]
        # Communication distance between nodes
        self.Dist = [[0,1,1,1],[1,0,1,1],[1,1,0,1],[1,1,1,0]]

    # To calculate the distance between container i and j
    def containerDistance(self,i,j):
        m = -1
        n = -1
        m = self.container_state_queue[i]
        n = self.container_state_queue[j]

        p = service_container_relationship[i]
        q = service_container_relationship[j]

        if self.Dist[ m ] [n ] != 0 and (p != q):
            container_dist = self.Dist[ m ][ n ]
        else:
            container_dist = 0
        return container_dist

    # To calculate the communication cost between container i and j
    def commCost(self,i,j):
        cost = 0
        interaction = self.service_weight[i][j] / (service_containernum[i] * service_containernum[j])
        for k in range ( len(service_container[i]) ):
            for l in range (len(service_container[j]) ):
                cost += self.containerDistance(service_container[i][k],service_container[j][l]) * interaction
        return cost

    def sumCommCost(self):
        Cost = 0
        for i in range (ServiceNumber):
            for j in range (ServiceNumber):
                Cost += self.commCost(i,j)   
        return 0.5 * Cost

    def calcVar(self):
        NodeCPU = []
        NodeMemory = []
        Var = 0
        for i in range(NodeNumber):
            U =  self.node_state_queue[i*(ContainerNumber+2)+ContainerNumber] 
            M = self.node_state_queue[i*(ContainerNumber+2)+ (ContainerNumber+1)]
            NodeCPU.append(U)
            NodeMemory.append(M)
            # if NodeCPU[i] > 1 or NodeMemory[i] > 1:
            #     Var -= 10  
        # Variance of node load
        Var += beta[0] * np.var(NodeCPU) + beta[1] * np.var(NodeMemory)
        return Var

    def getJointcost(self):
        re = 0
        g1 = self.sumCommCost()
        g1 = g1 / 4
        g2 = self.calcVar()
        g2 = g2 / 0.052812500000000005
        re += alpha *  g1  + (1-alpha) *  g2 
        return 100*re,g1,g2

    def state_update(self,container_state_queue,node_state_queue):
        self.State = container_state_queue + node_state_queue
        #print(self.State)

    # update state
    def update(self):
        if self.action[0] >= 0 and self.action[1] >= 0:
            app,version = getContainerDetails(self.action[1])
            nodeName = getNodeName(self.action[0])
           # print('update state',self.action)
            
            # update container state
            self.container_state_queue[ self.action[1]] = self.action[0] 
            
            # update node state
            self.node_state_queue[ self.action[0] * (ContainerNumber+2) + self.action[1] ] = 1

            #CPU and memory 
            self.node_state_queue[ self.action[0] * (ContainerNumber+2) + ContainerNumber] = getCpuUsagePercentage(nodeName)/100
            self.node_state_queue[ self.action[0] * (ContainerNumber+2) + (ContainerNumber + 1) ] = getMemoryUsagePercentage(nodeName)/100
            
            self.action_queue.append(self.action)

            #calling deploy function to apply yaml file
            deploy(app,version,nodeName)
        else:
            print("invalid action")  
            self.node_state_queue = []
            self.container_state_queue = []
            self.action_queue = []

            self.prepare()  
        self.state_update(self.container_state_queue,self.node_state_queue)
        return self.State

    # input: action(Targetnode，ContainerIndex)
    # output: next state, cost, done
    def step(self,action):
        global count
        self.action = self.index_to_act(action)
        self.update()
        cost,comm,var = self.getJointcost()   
        #print("Joint cost",cost,comm,var)
        done = False 
        count = 0
        
        for i in range(ContainerNumber):
            if self.container_state_queue[i] != -1:
                count += 1
        if count == ContainerNumber:
            done = True
        return self.State , cost , done,comm ,var

    def reset(self):
        self.node_state_queue = []
        self.container_state_queue = []
        self.prepare() 
        return self.State,self.action
    
    def index_to_act(self, index):
        act = [-1,-1]
        act[0] = int(index / ContainerNumber)
        act[1] = index % ContainerNumber
        return act