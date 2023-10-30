import docker

def run_containers(client, len):

    containers = {}

    for num in range(len):
        mavlink_container_id = client.containers.run("test_mavlink", ["python", "measure_square.py"], detach=True).id
        mavlink_container = client.containers.get(mavlink_container_id)
        # mavlink コンテナのIPアドレスを取得
        mavlink_container_ip = mavlink_container.attrs['NetworkSettings']['IPAddress']
        # print(f"mavlink コンテナのIPアドレス: {mavlink_container_ip}")

        command = f'bash -c "(SITL_RITW_TERMINAL=bash /ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter --no-mavproxy --sim-address=$(hostname -i) &) | .local/bin/mavproxy.py  --out {mavlink_container_ip}:14551 --master tcp:$(hostname -i):5760 --sitl $(hostname -i):5501"'
        sitl_container_id = client.containers.run("test_ardupilot_sitl_gui", command, tty=True, detach=True).id
        sitl_container = client.containers.get(sitl_container_id)
        # sitl コンテナのIPアドレスを取得
        sitl_container_ip = sitl_container.attrs['NetworkSettings']['IPAddress']
        # print(f"sitl コンテナのIPアドレス: {sitl_container_ip}")


        print(f"containers: {num} | mavlink_ip: {mavlink_container_ip} | sitl_ip: {sitl_container_ip}")

        containers.setdefault(mavlink_container_id, [mavlink_container_id, sitl_container_id])
    
    return containers


def main():
    client = docker.from_env()
    len = 10
    print(f"start integrate {len} containers")

    containers = run_containers(client, len)

    # イベントストリームを開始
    events = client.events(decode=True)

    try:
        count = 0

        for event in events:
            if event['Type'] == 'container' and event['Action'] == 'die':
                container_id = event['id']
                # exit_code = event['Actor']['Attributes']['exitCode']

                if(container_id in containers.keys()):
                    # print(f"mavlink コンテナ {container_id} が終了しました")

                    mavlink_container_id = containers[container_id][0]
                    sitl_container_id = containers[container_id][1]
                    # containers.pop(container_id)

                    mavlink_container = client.containers.get(mavlink_container_id)
                    mavlink_container_ip = mavlink_container.attrs['NetworkSettings']['IPAddress']
                    print(f"{mavlink_container_ip}: {client.containers.get(mavlink_container_id).logs()}")
                    
                    client.containers.get(mavlink_container_id).stop()
                    client.containers.get(mavlink_container_id).remove()
                    client.containers.get(sitl_container_id).stop()
                    client.containers.get(sitl_container_id).remove()

                    count = count + 1
                    if count == len:
                        print(f"end {len} mavlink containers")
                        break

    except KeyboardInterrupt:
        # Ctrl+C などでプログラムを停止
        for container_id in containers:
            mavlink_container_id = containers[container_id][0]
            sitl_container_id = containers[container_id][1]
            client.containers.get(mavlink_container_id).stop()
            client.containers.get(mavlink_container_id).remove()
            client.containers.get(sitl_container_id).stop()
            client.containers.get(sitl_container_id).remove()
            
        pass
    finally:
        events.close()
        print(f"end integrate {len} containers")
            

if __name__ == "__main__":
    main()