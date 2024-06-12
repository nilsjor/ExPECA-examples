



Create the server node
```
edgenet = chi.network.get_network("edge-net")
container_name = "bryan-ct-server-node"
chi.container.create_container(
    name = container_name,
    image = "samiemostafavi/perf-meas",
    reservation_id = worker_reservation_id,
    environment = {},
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
