from dronekit import connect, VehicleMode, LocationGlobalRelative
from video_tracking.camera import Camera
from range_finder.lidar_lite import Lidar_Lite
import time
import argparse  
import math



# DEFINITIONS #########################################################################################################

class Position:
  '''Define a position:
      -latitude: lat (global coord)
      -longitude: lon (global coord)
      -altitude: alt (relative coord)'''
      
  def __init__(self, latitude, longitude, altitude)
    self.lat = latitude
    self.lon = longitude
    self.alt = altitude



#TakeOff command
def arm_and_takeoff(aTargetAltitude):
    # Arms vehicle and fly to aTargetAltitude.

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise... Vehicle is not armable yet"
        time.sleep(1)

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True    

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt 
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: 
            print "Reached target altitude"
            break
        time.sleep(1)


def goto(vehicle, position)
# WARNING: doesn't work for a mooving platform
  Re = 6371000
  timer = 0
  uav_pos = vehicle.location.global_relative_frame
  plat_pos = position
  
  vehicle.simple_goto(plat_pos)
  
  while (get_distance_metres(uav_pos, plat_pos)<1.5) and (timer < 20):
  #(math.sqrt(((uav_pos.lat-plat_pos.lat)*Re*math.pi/180)**2 + ((uav_pos.lon-plat_pos.lat)*Re*math.pi/180)**2) < 1.5) && (timer < 20):
    time.sleep(0.5)
    timer = timer + 0.5
    uav_pos = vehicle.location.global_relative_frame


#Velocity command
def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on specified velocity vectors.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)




# MAIN #####################################################################################################

#Set up option parsing to get connection string
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
target_altitude=4


#Return error if no connection found
if not args.connect:
    print "No connected vehicle"


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True)


#Take off
arm_and_takeoff(target_altitude)

print "Set default/target airspeed to 3"
vehicle.airspeed = 3

#Get GPS from platform
#######################################################
#See with the guys DON'T FORGET TO FILTER TO AVOID JUMPS
latitude = 52.073743
longitude = -0.630707
altitude = 4
platform_pos = LocationGlobalRelative(52.073743, -0.630707, 4)
#######################################################


while True:
  #Travel toward the target
  goto(vehicle, platform_pos)
  
  #Init the tracking camera
  tracker = Camera()
  counter = 0

    while True:
      #try to get target coordinates, returns None if target not found
      (yT, xT, img_width, img_height) = tracker.seek_target # quadcopter frame: y=horizontal 
      #axis (right pos), x=vertical axis (top pos)
      if ((xT, yT) == (None, None):
        if counter == 5
          counter = 0
          break
        else:
          counter = counter+1
      else:
        counter = 0
        roi = locationGlobalRelative(vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon, -100)
        vehicle.gimbal.target_location(vehicle.vehicle.location.global_relative_frame)
        #The camera is turned toward the ground and the coord
        #frame of the image is the same as the coord frame of 
        #the quadcopter horizontal plane (small angles approx)
        
        ###############################################
        #Get altitude with lidar
        alt = vehicle.location.global_relative_frame.alt
        ###############################################
        
        yT = yT-img_width/2
        xT = xT-img_height/2
        vy_targ =  max(yT/150*alt, 1) # move slower at reduce altitude
        vx_targ = max(xT/150*alt, 1)
        vz_targ = -max(1/sqrt((xT/150)**2 + (yT/150)**2), 0.15) 
        #the closer it is to the target the faster it goes down, limited to 0.15m/s


#######################################################
#Add landing algorithm HERE
#######################################################



#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

