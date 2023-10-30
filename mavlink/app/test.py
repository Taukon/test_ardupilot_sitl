import socket
import time
import sys
from pymavlink import mavutil


# this program assumes that there are 3 vehicles participating in coordinated flight with sys is 1 - 3

def set_flight_mode(con, mode, target_sysid=1):
    # Check if mode is available
    if mode not in con.mode_mapping():
        print(f'Unknown mode : {mode}')
        print(f"available modes: {list(con.mode_mapping().keys())}")
        return 1

    # Get mode ID
    mode_id = con.mode_mapping()[mode]

    con.mav.command_long_send(target_sysid, con.target_component, mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                             0, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id, 0, 0, 0, 0, 0)


    time_start = time.time()
    while time.time() - time_start < 3:
        ack_msg = con.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        print(ack_msg, mavutil.mavlink.MAV_CMD_DO_SET_MODE)
        if ack_msg:
            # Continue waiting if the acknowledged command is not `set_mode`
            if ack_msg.command != mavutil.mavlink.MAV_CMD_DO_SET_MODE:
                continue
            else:
                print('set mode ack')
                # Print the ACK result !
                print(mavutil.mavlink.enums['MAV_RESULT']
                    [ack_msg.result].description)
                return 0
    return 1

def takeoff(con, alt, target_sysid=1):
    con.mav.command_long_send(target_sysid, con.target_component,
                              mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

    msg = con.recv_match(type='COMMAND_ACK', blocking=True)
    if msg.result != 0:
        print(f"Error arming drone. arm request returned {msg.result}")
        return 1
    else:
        print(f"drone sysid {target_sysid} armed successfully")

    con.mav.command_long_send(target_sysid, con.target_component,
                              mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 25, 0, 0, alt)

    msg = con.recv_match(type='COMMAND_ACK', blocking=True)
    if msg.result != 0:
        print(
            f"Error requesting takeoff drone. takeoff request returned {msg.result}")
        return 1
    else:
        print(f"drone sysid {target_sysid} took off successfully")
        return 0


def goto_ned(con, wp, target_sysid=1):
    con.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, target_sysid, 1,
                                                                               mavutil.mavlink.MAV_FRAME_LOCAL_NED, int(0b110111111000), wp[0], wp[1], wp[2], 0, 0, 0, 0, 0, 0, 1.5, 0))


def check_reached(con, wp, target_sysid=1):

    while 1:
        msg = con.recv_match(type='LOCAL_POSITION_NED', blocking=True)
        if msg.get_srcSystem() == target_sysid:
            print(msg)
            if (abs(msg.x - wp[0]) < 0.5) and (abs(msg.y - wp[1]) < 0.5) and (abs(msg.z - wp[2]) < 0.5):
                return 1
            else:
                return 0

def land(con, target_sysid=1):
    con.mav.command_long_send(con.target_system, con.target_component,
                                     mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 25, 0, 0, 0)
    msg = con.recv_match(type='COMMAND_ACK', blocking=True)
    print(msg)

    if msg.result != 0:
        print(
            f"Error requesting takeoff drone. land request returned {msg.result}")
        return -1
    else:
        print(f"drone sysid {target_sysid} land successfully")


def main():

    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    # print('ip address: '+ip)
    
    # Start a connection listening to a UDP port
    con = mavutil.mavlink_connection('udpin:'+ip+':14551')

    con.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" %
          (con.target_system, con.target_component))
    
    sysid = con.target_system
    
    if set_flight_mode(con, 'GUIDED', target_sysid=sysid) == 1:
        print('fail set flight mode')
        sys.exit(1)

    if takeoff(con, 10, target_sysid=sysid) == 1:
        count = 100
        while count > 0:
            time.sleep(2)
            if takeoff(con, 10, target_sysid=sysid) != 1:
                break
            count = count - 1
        if count == 0:
            sys.exit(1)

    # takeoff(con, 10, target_sysid=sysid)

    time.sleep(10)

    aircraft1_wp = [-10, 10, -10]
    goto_ned(con, aircraft1_wp, sysid)
    

    aircraft1_ready = 0
    while 1:
        if check_reached(con, aircraft1_wp, sysid):
            aircraft1_ready = 1
        
        if aircraft1_ready:
            print("all aircraft at destination")
            land(con, sysid)
            break


if __name__ == "__main__":
    main()