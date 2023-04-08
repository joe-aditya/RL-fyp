from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url='http://localhost:9090', disable_ssl=True)

def getCpuUsagePercentage(nodeName: str):
    query = f'avg(rate(node_cpu_seconds_total{{mode!="idle", node="{nodeName}"}}[2m])) by (node) * 1000'
    
    results = prom.custom_query(query=query)

    return float(results[0]['value'][1])


def getMemoryUsagePercentage(nodeName: str):
    query = f'(1 - (node_memory_MemAvailable_bytes{{node="{nodeName}"}} / node_memory_MemTotal_bytes{{node="{nodeName}"}})) * 100'

    results = prom.custom_query(query=query)

    return float(results[0]['value'][1])


if __name__ == '__main__':
    import mappings

    print('\n------------Usage Statistics------------\n')
    for nodeNumber in mappings.nodeNumberToName:
        nodeName = mappings.nodeNumberToName[nodeNumber]
        cpu = getCpuUsagePercentage(nodeName)
        memory = getMemoryUsagePercentage(nodeName)
        print(f'{nodeNumber}. {nodeName} -> cpu={cpu:.2f}%, memory={memory:.2f}%')