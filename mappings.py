containerNumberToDetails = {
    0: {'app': 'productpage', 'version': 'v1'},
    1: {'app': 'details', 'version': 'v1'},
    2: {'app': 'reviews', 'version': 'v1'},
    3: {'app': 'reviews', 'version': 'v2'},
    4: {'app': 'reviews', 'version': 'v3'},
    5: {'app': 'ratings', 'version': 'v1'}
}

nodeNumberToName = {
    0: 'gke-cluster-1-default-pool-a33b274c-c0j2',
    1: 'gke-cluster-1-default-pool-a33b274c-p7jv',
    2: 'gke-cluster-1-default-pool-a33b274c-r20s',
    3: 'gke-cluster-1-default-pool-a33b274c-s7tw',
}

def getNodeName(nodeNumber: int):
    return nodeNumberToName[nodeNumber]

def getContainerDetails(containerNumber: int):
    d = containerNumberToDetails[containerNumber]
    return d['app'], d['version']