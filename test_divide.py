import docker

def run_containers(client, len):

    containers = {}

    for num in range(len):
        mavlink_container_id = client.containers.run("test_mavlink", ["python", "measure_square.py"], detach=True).id
        mavlink_container = client.containers.get(mavlink_container_id)
        # mavlink コンテナのIPアドレスを取得
        mavlink_container_ip = mavlink_container.attrs['NetworkSettings']['IPAddress']
        # print(f"mavlink コンテナのIPアドレス: {mavlink_container_ip}")

        sitl_container_id = client.containers.run("test_ardupilot_sitl", detach=True).id
        sitl_container = client.containers.get(sitl_container_id)
        # sitl コンテナのIPアドレスを取得
        sitl_container_ip = sitl_container.attrs['NetworkSettings']['IPAddress']
        # print(f"sitl コンテナのIPアドレス: {sitl_container_ip}")


        command = f'.local/bin/mavproxy.py  --out {mavlink_container_ip}:14551 --master tcp:{sitl_container_ip}:5760 --sitl {sitl_container_ip}:5501'
        mavproxy_container_id = client.containers.run("test_mavproxy", command, tty=True, detach=True).id
        mavproxy_container = client.containers.get(mavproxy_container_id)
        # mavproxy コンテナのIPアドレスを取得
        mavproxy_container_ip = mavproxy_container.attrs['NetworkSettings']['IPAddress']
        # print(f"mavproxy コンテナのIPアドレス: {mavproxy_container_ip}")

        print(f"containers: {num} | mavlink_ip: {mavlink_container_ip} | sitl_ip: {sitl_container_ip} | mavproxy_ip: {mavproxy_container_ip}")

        containers.setdefault(mavlink_container_id, [mavlink_container_id, sitl_container_id, mavproxy_container_id])
    
    return containers


def main():
    client = docker.from_env()
    len = 20
    print(f"start divide {len} containers")

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
                    mavproxy_container_id = containers[container_id][2]
                    # containers.pop(container_id)
                    
                    mavlink_container = client.containers.get(mavlink_container_id)
                    mavlink_container_ip = mavlink_container.attrs['NetworkSettings']['IPAddress']
                    print(f"{mavlink_container_ip}: {client.containers.get(mavlink_container_id).logs()}")
                    
                    client.containers.get(mavlink_container_id).stop()
                    client.containers.get(mavlink_container_id).remove()
                    client.containers.get(sitl_container_id).stop()
                    client.containers.get(sitl_container_id).remove()
                    client.containers.get(mavproxy_container_id).stop()
                    client.containers.get(mavproxy_container_id).remove()

                    count = count + 1
                    if count == len:
                        break

    except KeyboardInterrupt:
        # Ctrl+C などでプログラムを停止
        for container_id in containers:
            mavlink_container_id = containers[container_id][0]
            sitl_container_id = containers[container_id][1]
            mavproxy_container_id = containers[container_id][2]
            client.containers.get(mavlink_container_id).stop()
            client.containers.get(mavlink_container_id).remove()
            client.containers.get(sitl_container_id).stop()
            client.containers.get(sitl_container_id).remove()
            client.containers.get(mavproxy_container_id).stop()
            client.containers.get(mavproxy_container_id).remove()
        pass
    finally:
        events.close()
        for container_id in containers:
            mavlink_container_id = containers[container_id][0]
            client.containers.get(mavlink_container_id).stop()
            client.containers.get(mavlink_container_id).remove()
        print(f"end divide {len} containers")
            

if __name__ == "__main__":
    main()