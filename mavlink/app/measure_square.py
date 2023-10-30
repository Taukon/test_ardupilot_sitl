import time
import sys
from pymavlink import mavutil
import socket

def set_flight_mode(connection, mode, target_sysid):
    # Check if mode is available
    if mode not in connection.mode_mapping():
        print(f'Unknown mode : {mode}')
        print(f"available modes: {list(connection.mode_mapping().keys())}")
        return 1

    # Get mode ID
    mode_id = connection.mode_mapping()[mode]

    connection.mav.command_long_send(target_sysid, connection.target_component, mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                             0, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id, 0, 0, 0, 0, 0)


    time_start = time.time()
    while time.time() - time_start < 3:
        ack_msg = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        # print(ack_msg, mavutil.mavlink.MAV_CMD_DO_SET_MODE)
        if ack_msg:
            # Continue waiting if the acknowledged command is not `set_mode`
            if ack_msg.command != mavutil.mavlink.MAV_CMD_DO_SET_MODE:
                continue
            else:
                # print('set mode ack')
                return 0
    return 1

def arm(connection, target_sysid):
    connection.mav.command_long_send(target_sysid, connection.target_component,
                                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
    # print(msg)
    if msg.result != 0:
        # print(f"Error arming drone. arm request returned {msg.result}")           
        return 1
    else:
        # print(f"drone sysid {target_sysid} armed successfully")
        return 0

def takeoff(connection, alt, target_sysid):
    connection.mav.command_long_send(target_sysid, connection.target_component,
                                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 25, 0, 0, alt)
        
    msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
    # print(msg)
    if msg.result != 0:
        # print(f"Error requesting takeoff drone. takeoff request returned {msg.result}")
        return 1
    else:
        # print(f"drone sysid {target_sysid} take off successfully")
        return 0
    
def run_drone(connection, alt, target_sysid):
    count = 100
    while count > 0:
        if set_flight_mode(connection, 'GUIDED', target_sysid) == 0:
            if arm(connection, target_sysid) == 0:
                if takeoff(connection, alt, target_sysid) == 0:
                    print("run drone")
                    return 0
                
        time.sleep(3)
        count = count -1

    return 1

def check_alt_reached(connection, alt, target_sysid):
    msg = connection.recv_match(type='LOCAL_POSITION_NED', blocking=True)
    if msg.get_srcSystem() != target_sysid:
        return 0
    
    # print(msg)
    if abs(msg.z - (-alt)) < 1:
        return 1
    else:
        return 0


def check_reached(connection, target_sysid):
    msg = connection.recv_match(type='NAV_CONTROLLER_OUTPUT', blocking=True)
    if msg.get_srcSystem() != target_sysid:
        return 0

    # print(msg)
    if (msg.wp_dist < 1):
        return 1
    else:
        return 0


def set_new_wp_ned(connection, wp_ned, target_sysid):
    connection.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, target_sysid, connection.target_component,
                                                                                          mavutil.mavlink.MAV_FRAME_LOCAL_NED, int(0b110111111000), wp_ned[0], wp_ned[1], wp_ned[2], 0, 0, 0, 0, 0, 0, 1.5, 0))
    while 1:
        msg = connection.recv_match(
            type='NAV_CONTROLLER_OUTPUT', blocking=True)
        if msg.wp_dist > 0:
            break


def main():

    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    # print('ip address: '+ip)
    
    # Start a connection listening to a UDP port
    the_connection = mavutil.mavlink_connection('udpin:'+ip+':14551')

    # Wait for the first heartbeat
    #   This sets the system and component ID of remote system for the link
    the_connection.wait_heartbeat()
    
    time_start = time.time()

    # print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

    alt = 10
    if run_drone(the_connection, alt, the_connection.target_system) == 1:
        print('fail set drone')
        sys.exit(1)

    while 1:
        if check_alt_reached(the_connection, alt, the_connection.target_system):
            # print("takeoff reached")
            break


    wp_arr = []
    wp_arr.append([10, 0, -10])
    wp_arr.append([10, 10, -10])
    wp_arr.append([0, 10, -10])
    wp_arr.append([0, 0, -10])

    wp_num = 0
    for wp in wp_arr:
        set_new_wp_ned(the_connection, wp, the_connection.target_system)
        while 1:
            if check_reached(the_connection, the_connection.target_system):
                break
        wp_num = wp_num + 1

    the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                        mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0)
    
    time.time() - time_start
    print(" drone run time: " + str(time.time() - time_start) + " ")

if __name__ == "__main__":
    main()