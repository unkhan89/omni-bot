
'''
Http Interface for controlling Servos and 4 directional platform.
Executable file, unlike controller_gui that needs instantiation.

Expected hardware setup for platform:
        
        S1
    S4      S2
        S3

'''
 
import logging as log
import time
import thread
import traceback
import datetime
import cv2
import opencv_utils
from flask import *
from config import settings
from src.psc import PSC


app = Flask("Web Controller", static_folder='static')    
dev = None
global shared_mem
shared_mem = {}


######################### paths ##################################

@app.route("/")
def controller():
    log.debug("GET /")
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/start")
def start_application():
    app_name = request.args.get('app')

    if app_name == 'ball_tracker' or app_name == 'ballTracker':
        try:
            app_name = 'ball_tracker'
            mode = request.args.get('mode')            
            if mode is None:
                return "No mode provided", 400
            
            color_to_track = request.args.get('color')
            if color_to_track is None:
                color_to_track = opencv_utils.COLOR_GREEN

            ui_enabled = False
            if request.args.get('ui_enabled') is not None or request.args.get('ui') is not None:
                ui_enabled = True

            params = {
                'log' : log,
                'video_capture_device_id' : settings['web_cam_device_id'],
                'color_to_track' : color_to_track,
                'mode' : mode,
                'ui_enabled' : ui_enabled,
                'psc' : dev
            }
            global shared_mem
            import src.ball_tracker
            thread_id = thread.start_new_thread(ball_tracker.start, ('ball_tracker', params, shared_mem))
            message = "Started '" + app_name + "' application (thread id " + str(thread_id) + ")"
            log.info(message)
            return message
        
        except Exception, e:
            log.error("Error starting thread \n" + traceback.format_exc())
            return "Unable to start '" + app_name + "' application", 500
    else:
        return "Unknown application '" + str(app_name) + "'", 400
           

@app.route("/stop")
def stop_application():
    app_name = request.args.get('app')

    if app_name == 'ball_tracker':
        try:
            global shared_mem
            shared_mem[app_name] = "STOP"
            message = "Stopping '" + app_name + "' application"
            log.info(message)
            return message

        except Exception, e:
            log.error("Error stopping '" + app_name + "' application")
            return "Unable to stop '" + app_name + "' application", 500
    
    else:
        return "Unknown application '" + str(app_name) + "'", 400


@app.route('/move')
def move():
    ''' Moves the platform in a particular direction '''
    try:
        log.debug("GET /move")
        direction = request.args.get('direction')
        
        if direction is None or is_platform_direction_valid == False:
            return "Bad Reqeust - Please provide a valid move direction", 400
        
        log.debug("Requested: Move platform " + direction)
        
        if direction == "forward":
            rotate_servo(1, "idle")            
            rotate_servo(2, "clockwise")
            rotate_servo(3, "idle")
            rotate_servo(4, "counter_clockwise")
        
        elif direction == "backward":
            rotate_servo(1, "idle")            
            rotate_servo(2, "counter_clockwise")            
            rotate_servo(3, "idle")            
            rotate_servo(4, "clockwise")
            
        elif direction == "right":
            rotate_servo(1, "counter_clockwise")
            rotate_servo(2, "idle")            
            rotate_servo(3, "clockwise")
            rotate_servo(4, "idle")            
            
        elif direction == "left":
            rotate_servo(1, "clockwise")
            rotate_servo(2, "idle")                        
            rotate_servo(3, "counter_clockwise")
            rotate_servo(4, "idle")            
        
        elif direction == "stop":
            rotate_servo(1, "idle")
            rotate_servo(2, "idle")
            rotate_servo(3, "idle")
            rotate_servo(4, "idle")            
        
        else:
            return "Bad Request - Unknown direction", 400
        
        return "1"
    except Exception, e:
        log.error("Error controlling device\n" + traceback.format_exc())
        return "Internal Server Error", 500


@app.route('/rotate')
def rotate():
    ''' Rotates the platform in a particular direction '''
    try:
        log.debug("GET /rotate")
        direction = request.args.get('direction')
        
        if direction is None or is_platform_rotation_valid == False:
            return "Bad Reqeust - Please provide a valid rotational direction", 400
        
        log.debug("Requested: Rotate platform, direction = " + direction)
        
        if direction == "clockwise":
            rotate_servo(1, "counter_clockwise")
            rotate_servo(2, "counter_clockwise")
            rotate_servo(3, "counter_clockwise")
            rotate_servo(4, "counter_clockwise")
            
        elif direction == "counter_clockwise":
            rotate_servo(1, "clockwise")
            rotate_servo(2, "clockwise")
            rotate_servo(3, "clockwise")
            rotate_servo(4, "clockwise")
            
        elif direction == "stop":
            rotate_servo(1, "idle")
            rotate_servo(2, "idle")
            rotate_servo(3, "idle")
            rotate_servo(4, "idle")            
        
        else:
            return "Bad Request - Unknown direction", 400
        
        return "1"
    except Exception, e:
        log.error("Error controlling device\n" + traceback.format_exc())
        return "Internal Server Error", 500


@app.route('/rotateservo')
def rotateServo():
    try:
        log.debug("GET /rotateservo")
        servo = request.args.get('servo') 
        direction = request.args.get('direction')
        
        if (
            servo is None or 
            servo == "" or 
            is_parsable_to_int(servo) == False or 
            direction is None or 
            direction == ""
            ):
            log.warn('Bad request, please provide servo and direction')
            return "Bad Reqeust - Servo and/or direction not provided", 400
        
        log.debug("Requested: servo = " + servo + ", direction = " + direction)
        servo = int(float(servo))
            
        if is_servo_valid(servo, True) == False:
            return "Bad Request - Servo not found", 400
        
        direction = validate_servo_direction(direction)
        if direction is None:
            return "Bad Request - Unknown direction", 400
        
        return str(rotate_servo(servo, direction))
        
    except Exception, e:
        log.error("Error controlling device\n" + traceback.format_exc())
        return "Internal Server Error", 500


########################## functions ##############################


def rotate_servo(servo, direction):
    ''' Rotates an individual servo in the given direction '''
    log.debug("Controller_Web.control_device() servo = " + str(servo) + ", direction = " + direction)
    try:
        if dev.is_device_ready() == False:
            log.warn("Device is closed")
            return -1
        
        log.info("Sending command '" + str(direction) + "' to servo " + str(servo))
        
        if direction == "clockwise":
            dev.rotate_clockwise(servo)
        
        elif direction == "idle":
            dev.idle_cr_servo(servo)
        
        elif direction == "counter_clockwise":
            dev.rotate_counter_clockwise(servo)
        
        else:
            log.error("Unknown direction provided (" + str(direction) + "), should have never reached here")
            return "Internal Server Error"
        
        return 1   
        
    except Exception, e:
        log.error("Error in Controller_Web.control_device()\n" + traceback.format_exc())
        return -1


def is_platform_direction_valid(direction):
    ''' Checks whether the given direction is valid for the platform (forward, left, backwards, right) '''
    if (
        direction == "forward" or 
        direction == "left" or
        direction == "backward" or
        direction == "right" or
        direction == "stop"
        ):
        return True
    else:
        log.warn("is_platform_direction_valid(" + str(direction) + ") => False")
        return False 
    

def is_platform_rotation_valid(direction):
    ''' Checks whether the given rotation direction is valid for the platform (clockwise or counter-clockwise) '''
    if (
        direction == "clockwise" or 
        direction == "counter_clockwise" or
        direction == "stop"
        ):
        return True
    else:
        log.warn("is_platform_rotation_valid(" + str(direction) + ") => False")
        return False 


def validate_servo_direction(direction):
    ''' Checks whether the given direction is valid for a servo  '''
    if direction is None or direction == "":
        return None
    
    if direction.lower() == "clockwise" or direction == 1 or direction == "1":
        return "clockwise"
    
    if direction.lower() == "idle" or direction == 0 or direction == "0":
        return "idle"
    
    if (direction.lower() == "counter clockwise" or direction.lower() == "counter_clockwise"  
        or direction.lower() == "counter-clockwise" or direction == -1 or direction == "-1"
        ):
        return "counter_clockwise"
    
    # nothing matched, unknown direction
    return None


def is_servo_valid(servoChannel, expectingContinuousRotation):
    ''' Checks whether the given servo channel exists in config and is of expected type '''    
    for tempServo in settings['servo_setup']:
        if tempServo['channel'] == servoChannel:
            if tempServo['continuous_rotation'] and expectingContinuousRotation:
                return True
            elif tempServo['continuous_rotation'] == False and expectingContinuousRotation == False:
                return True
        
    return False

    
def is_parsable_to_int(someString):
    ''' Checks whether a given string can be parsed into an integer '''
    try:
        foo = int(float(someString))
        return True
    except:
        return False


def start_opencv(log):
    ''' OpenCV related tasks, to be started in separate thread '''    
    log.debug("Opening camera input")
    try:
        cap = cv2.VideoCapture(1)
        while(True):

            _, frame = cap.read()
            cv2.imshow('frame', frame)

            # check for escape to quit
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()
    except Exception, e:
       log.error("Error: unable to start thread \n" + traceback.format_exc())

    log.info("Goodbye")


########################## main ###################################

if __name__ == "__main__":
    
    log.basicConfig(level=settings['logging_level'], format='%(asctime)s | %(levelname)s | %(module)s:%(lineno)s | %(message)s')
    log.info('Hello')    
    
    # initialize servo controller 
    dev = PSC(log, settings['servo_setup'])
    dev.set_default_positions()


    log.info("Starting server")
    if settings['flask_debug'] == True:        
        app.debug = True

    app.run(host=settings['http']['host'], port=settings['http']['port'], use_reloader=False)
