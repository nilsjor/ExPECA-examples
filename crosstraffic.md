# Cross Traffic Setup

Reserve
1. worker-06 and worker-07
2. advantech routers 02,03,04,05,and 06

Create the server node on worker-06 with port ens1f1.
```
edgenet = chi.network.get_network("edge-net")
container_name = "bryan-ct-server-node"
chi.container.create_container(
    name = container_name,
    image = "samiemostafavi/perf-meas",
    reservation_id = worker06_reservation_id,
    environment = {"SERVER_DIR":"/tmp/"},
    mounts = [],
    nets = [
        { "network" : edgenet['id'] },
    ],
    labels = {
        "networks.1.interface":"ens1f1",
        "networks.1.ip":"10.70.70.210/24",
        "networks.1.routes":"172.16.0.0/16-10.70.70.1",
    },
)
chi.container.wait_for_active(container_name)
logger.success(f"created {container_name} container.")
```

Run 5 iperf instances to manage 5 client nodes
```
ports = [
    53301,
    53302,
    53303,
    53304,
    53305
]
container_name = "bryan-ct-server-node"
for port in ports:
    command = f"iperf3 -s -p {port}"
    result = chi.container.execute(
        container_ref=container_name,
        command="curl -s -X POST -H \"Content-Type: application/json\" -d '{\"cmd\": \"" + command + "\"}' http://localhost:50505/",
    )
    logger.info(f"{result}")
```

Create 5 client nodes:

1. worker-06 port eno12399np0 and adv-02
2. worker-06 port eno12409np1 and adv-03
3. worker-07 port ens1 and adv-04
4. worker-07 port eno12409 and adv-05
5. worker-07 port eno12419 and adv-06

Node-01:
```
advnet = chi.network.get_network("adv-02-net")
container_name = "bryan-ct-client-node-01"
chi.container.create_container(
    name = container_name,
    image = "samiemostafavi/perf-meas",
    reservation_id = worker06_reservation_id,
    environment = {"SERVER_DIR":"/tmp/"},
    nets = [
        { "network" : advnet['id'] },
    ],
    labels = {
        "networks.1.interface":"eno12399np0",
        "networks.1.ip":"10.42.3.2/24",
        "networks.1.routes":"10.70.70.0/24-10.42.3.1",
    },
)
chi.container.wait_for_active(container_name)
logger.success(f"created {container_name} container.")
```
Node-02:
```
advnet = chi.network.get_network("adv-03-netw")
container_name = "bryan-ct-client-node-02"
chi.container.create_container(
    name = container_name,
    image = "samiemostafavi/perf-meas",
    reservation_id = worker06_reservation_id,
    environment = {"SERVER_DIR":"/tmp/"},
    nets = [
        { "network" : advnet['id'] },
    ],
    labels = {
        "networks.1.interface":"eno12409np1",
        "networks.1.ip":"10.42.3.2/24",
        "networks.1.routes":"10.70.70.0/24-10.42.3.1",
    },
)
chi.container.wait_for_active(container_name)
logger.success(f"created {container_name} container.")
```

Node-03:
```
advnet = chi.network.get_network("adv-04-netw")
container_name = "bryan-ct-client-node-03"
chi.container.create_container(
    name = container_name,
    image = "samiemostafavi/perf-meas",
    reservation_id = worker07_reservation_id,
    environment = {"SERVER_DIR":"/tmp/"},
    nets = [
        { "network" : advnet['id'] },
    ],
    labels = {
        "networks.1.interface":"ens1",
        "networks.1.ip":"10.42.3.2/24",
        "networks.1.routes":"10.70.70.0/24-10.42.3.1",
    },
)
chi.container.wait_for_active(container_name)
logger.success(f"created {container_name} container.")
```

Node-04:
```
advnet = chi.network.get_network("adv-05-net")
container_name = "bryan-ct-client-node-04"
chi.container.create_container(
    name = container_name,
    image = "samiemostafavi/perf-meas",
    reservation_id = worker07_reservation_id,
    environment = {"SERVER_DIR":"/tmp/"},
    nets = [
        { "network" : advnet['id'] },
    ],
    labels = {
        "networks.1.interface":"eno12409",
        "networks.1.ip":"10.42.3.2/24",
        "networks.1.routes":"10.70.70.0/24-10.42.3.1",
    },
)
chi.container.wait_for_active(container_name)
logger.success(f"created {container_name} container.")
```

Node-05:
```
advnet = chi.network.get_network("adv-06-netw")
container_name = "bryan-ct-client-node-05"
chi.container.create_container(
    name = container_name,
    image = "samiemostafavi/perf-meas",
    reservation_id = worker07_reservation_id,
    environment = {"SERVER_DIR":"/tmp/"},
    nets = [
        { "network" : advnet['id'] },
    ],
    labels = {
        "networks.1.interface":"eno12419",
        "networks.1.ip":"10.42.3.2/24",
        "networks.1.routes":"10.70.70.0/24-10.42.3.1",
    },
)
chi.container.wait_for_active(container_name)
logger.success(f"created {container_name} container.")
```

You can test them by running `iperf3 -c 10.70.70.210 -u -b 1G` in their console.

```
ports = [
    53301,
    53302,
    53303,
    53304,
    53305
]
nodes_names = [
    "bryan-ct-client-node-01",
    "bryan-ct-client-node-02",
    "bryan-ct-client-node-03",
    "bryan-ct-client-node-04",
    "bryan-ct-client-node-05"
]

for container_name,port in zip(nodes_names,ports):
    command = "iperf3 -c 10.70.70.210 -p {port} -b 5M -t 30"
    result = chi.container.execute(
        container_ref=container_name,
        command="curl -s -X POST -H \"Content-Type: application/json\" -d '{\"cmd\": \"" + command + "\"}' http://localhost:50505/",
    )
    logger.info(f"{result}")
```
