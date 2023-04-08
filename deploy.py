import subprocess
import yaml

# labels = [(key1, value1), (key2, value2)]
def matchesAnyLabel(d,labels):
    for key, value in labels:
        if d.get(key) == value:
            return True
    return False


def hasLabel(d, label):
    key, value = label
    return d.get(key) == value


def isDeployment(d: dict):
    return d.get('kind') == 'Deployment'


# Get only the required configs from the config file that contains everything
def getRequiredConfigs(configFileName, app, version, nodeName):
    labels = [("app", app), ("account", app)]
    appConfigs = []
    
    with open(configFileName, 'r') as configFile:
        data = yaml.safe_load_all(configFile)
        for d in data:
            if d is None: break
            
            availableLabels = d['metadata']['labels']
            
            if not matchesAnyLabel(availableLabels, labels):
                continue
            
            if isDeployment(d):
                if not hasLabel(availableLabels, ("version", version)):
                    continue
                d['spec']['template']['spec']['nodeSelector'] = {'kubernetes.io/hostname': nodeName}
            appConfigs.append(d)
    
    return appConfigs



def deploy(app, version, nodeName):
    appConfigs = getRequiredConfigs('bookinfo.yaml', app, version, nodeName)

    with open(f'{app}-{version}.yaml', 'w') as outputFile:
        yaml.dump_all(appConfigs, outputFile)

    output = subprocess.run(['kubectl', 'apply', '-f', f'{app}-{version}.yaml'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return output


if __name__ == '__main__':
    app = 'reviews'
    version = 'v3'
    nodeName = 'gke-cluster-1-default-pool-a33b274c-s7tw'
    output = deploy(app, version, nodeName)
    print(output.stdout.decode())
    print(output.stderr.decode())