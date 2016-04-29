from dronekit import connect, VehicleMode, LocationGlobalRelative
import time


#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
target_altitude=5


#Return error if no connection found
if not args.connect:
    print "No connected vehicle"


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True)


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


#Take off
arm_and_takeoff(target_altitude)

print "Set default/target airspeed to 3"
vehicle.airspeed = 3



#######################################################
#Add destination calculation algorithm here
target_point = LocationGlobalRelative(-35.363244, 149.168801, 20)
#######################################################



#Travel toward the target
vehicle.simple_goto(target_point)



#######################################################
time.sleep(10)
vehicle.mode = VehicleMode("RTL")
#Add landing algorithm HERE
#######################################################



#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

