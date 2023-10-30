import socket
from pymavlink import mavutil

host = socket.gethostname()
ip = socket.gethostbyname(host)
# print('ip address: '+ip)

# Start a connection listening to a UDP port
the_connection = mavutil.mavlink_connection('udpin:'+ip+':14551')

# Wait for the first heartbeat
#   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" %
      (the_connection.target_system, the_connection.target_component))

while 1:
    msg = the_connection.recv_match(type='ATTITUDE', blocking=True)
    print(msg)