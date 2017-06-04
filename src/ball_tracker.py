
import cv2
import numpy
import time
import traceback
import thread
from config import settings
import logging as log
from opencv_utils import *


def start(app_name, params, shared_mem):
    ''' '''
    try:
        log = params['log']
        log.info("Starting '" + app_name + "' application")

        video_capture_device_id = 0     # the video device in /dev
        if 'video_capture_device_id' in params:
            video_capture_device_id = params['video_capture_device_id']

        color_to_track = COLOR_GREEN
        if 'color_to_track' in params:
            color_to_track = params['color_to_track']

        psc = None
        if 'psc' not in params:
            log.error("Cannot run '" + app_name + "' without 'psc'")
            thread.exit()
        else:
            psc = params['psc']
        log.debug("psc: " + str(type(psc)))

        mode = None
        PSC_WEB_CAM_ENABLED = False
        PSC_PLATFORM_ENABLED = False

        if 'mode' not in params:
            log.error("Cannot run '" + app_name + "' without 'mode'")
            thread.exit()
        else:
            if params['mode'] == 'track':
                PSC_WEB_CAM_ENABLED = True

            elif params['mode'] == 'follow':
                PSC_PLATFORM_ENABLED = True
                

        if PSC_PLATFORM_ENABLED == False and PSC_WEB_CAM_ENABLED == False:
            log.warn("Unknown mode provided: " + str(mode) + ", exiting application")
            thread.exit()

        UI_ENABLED = False
        if 'ui_enabled' in params:
            UI_ENABLED = params['ui_enabled']


        shared_mem[app_name] = ""

        #global SERVO_X_CHANNEL
        SERVO_X_CHANNEL = 14 
        #global SERVO_Y_CHANNEL
        SERVO_Y_CHANNEL = 15        
        #global position_servo_x
        position_servo_x = 750
        #global position_servo_y
        position_servo_y = 750
        #global psc_enabled

        if PSC_PLATFORM_ENABLED:
            # for follow mode of this app, it necessary the cam point slight downwrads
            psc.set_servo_position(SERVO_Y_CHANNEL, 910)
            


        # TODO Refactor into a utils module
        def rotate_servo(servo, direction):
            ''' Rotates an individual servo in the given direction '''
            log.debug("Controller_Web.control_device() servo = " + str(servo) + ", direction = " + direction)
            try:
                if psc.is_device_ready() == False:
                    log.warn("Device is closed")
                    return -1
                
                log.info("Sending command '" + str(direction) + "' to servo " + str(servo))
                
                if direction == "clockwise":
                    psc.rotate_clockwise(servo)
                
                elif direction == "idle":
                    psc.idle_cr_servo(servo)
                
                elif direction == "counter_clockwise":
                    psc.rotate_counter_clockwise(servo)
                
                else:
                    log.error("Unknown direction provided (" + str(direction) + "), should have never reached here")
                    return "Internal Server Error"
                
                return 1   
                
            except Exception, e:
                log.error("Error in Controller_Web.control_device()\n" + traceback.format_exc())
                return -1

        
        # funcitons for simluating the psc controlling web cam servos
        '''
        def get_servo_position(channel):
            global SERVO_X_CHANNEL
            global SERVO_Y_CHANNEL
            global position_servo_x
            global position_servo_y
            if channel == SERVO_X_CHANNEL:
                return position_servo_x
            elif channel == SERVO_Y_CHANNEL:
                return position_servo_y

        def set_servo_position(channel, position):
            global SERVO_X_CHANNEL
            global SERVO_Y_CHANNEL
            global position_servo_x
            global position_servo_y
            if channel == SERVO_X_CHANNEL and position > 300 and position < 1200:
                position_servo_x = position        
            elif channel == SERVO_Y_CHANNEL and position > 300 and position < 1200:
                position_servo_y = position
        '''

        log.debug("Opening device id " + str(video_capture_device_id) )
        cap = cv2.VideoCapture(video_capture_device_id)

        # TODO optimize this?
        kernel = numpy.ones((3, 3), numpy.uint8)


        ''' FOLLOW MODE can have one of three valid states: rotating, following, stopped '''
        # TODO Document states
        state = "unknown"

        last = time.time()
        while(True):
            
            current = time.time()
            log.error("Iteration  " + str(current-last)  )
            last = time.time()
            
            
            # Take each frame
            _, frame = cap.read()
            
            # Convert BGR to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Threshold the HSV image to get only blue colors
            mask = cv2.inRange(hsv, color_to_track['lower_bound'], color_to_track['upper_bound'])

            # erode
            eroded = cv2.erode(mask, kernel)
            
            # dialate
            dilated = cv2.dilate(eroded, kernel)
            
            # find all the contours of all the matchings
            contours_list, hierarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            print("opencv took " + str( time.time() - last   )  )
            
            # find contours and draw on frame 
            if len(contours_list) > 0:
                largest_contour = contours_list[0]  # assume first one until largest found
                for con in contours_list:
                    #print( "> size: " + str(con.size) )
                    if con.size > largest_contour.size:
                        largest_contour = con
                        
                #print("largest_contour = " + str(largest_contour.size))
                if largest_contour.size > 950:
                    log.info("Ball in front")

                corners_nd3 = get_corner_coordinates(largest_contour)
                
                
                ''' Draw an X on target '''
                #padding_px = 75  
                #top_left = (corners_nd3[0][0][0], corners_nd3[0][0][1])
                #bottom_right = (corners_nd3[1][0][0], corners_nd3[1][0][1])
                #cv2.line(frame, top_left, bottom_right, (0, 0, 255), thickness=3)
                #top_right = (bottom_right[0] , top_left[1])
                #bottom_left = (top_left[0], bottom_right[1])
                #cv2.line(frame, bottom_left, top_right, (0, 0, 255), thickness=3)

                ''' Draw a rectangle partially around target '''
                #padding_px = 75  
                #top_left = (corners_nd3[0][0][0]-padding_px, corners_nd3[0][0][1])
                #bottom_right = (corners_nd3[1][0][0]+padding_px, corners_nd3[1][0][1])
                #cv2.rectangle(frame, top_left, bottom_right, COLOR_GREEN['bgr'], 2)
                
                ''' Draw a circle on target '''
                top_left = (corners_nd3[0][0][0], corners_nd3[0][0][1])
                bottom_right = (corners_nd3[1][0][0], corners_nd3[1][0][1])        
                target = ( (top_left[0] + bottom_right[0])/2, (top_left[1] + bottom_right[1])/2 )
                #cv2.circle(frame, target, 5, (0,0,255), thickness=10)
                #print("Target: " + str(target))
                to_move = get_next_move((frame.shape[1], frame.shape[0]), target)
                # note frame.shape[0] refers to number of rows in ndarray, thus the number of pixels on the y axis
                # and therefore frame[1] equals the number of pixels in the x dimension 
                

                ''' Draw square around center 
                frame_size = (frame.shape[1], frame.shape[0])
                threshold_x = 120
                threshold_y = 95
                center_x = frame_size[0]/2
                center_y = frame_size[1]/2
                top_left = (center_x - threshold_x, center_y - threshold_y)
                bottom_right = (center_x + threshold_x, center_y + threshold_y)
                cv2.rectangle(frame, top_left, bottom_right, COLOR_GREEN['bgr'], 2)
                '''

                ''' TRACK MODE : Send command to PSC to set camera servos to follow target '''
                if PSC_WEB_CAM_ENABLED:
                    if to_move[0] == 0 and to_move[1] == 0:
                        #print("On target")
                        to_move = None
                    
                    else:
                        global SERVO_X_CHANNEL
                        global SERVO_Y_CHANNEL
                        
                        #global position_servo_x
                        #global position_servo_y
                        
                        POSITION_FACTOR_X = 16
                        POSITION_FACTOR_Y = 10

                        #print("Not on target, to_move = " + str(to_move))
                        #print("position_servo_x = " + str(position_servo_x)) 
                        if to_move[0] == -1:          # target_x_status = -1, target < center

                            current_position = psc.get_servo_position(SERVO_X_CHANNEL) 
                            new_position = current_position - POSITION_FACTOR_X
                            psc.set_servo_position(SERVO_X_CHANNEL, new_position)  
                            log.info("Turning left > Old position " + str(current_position) + ", New position " + str(new_position))
                            
                        
                        elif to_move[0] == 1:         # target_x_status = 1, center < target
                            
                            current_position = psc.get_servo_position(SERVO_X_CHANNEL) 
                            new_position = current_position + POSITION_FACTOR_X
                            psc.set_servo_position(SERVO_X_CHANNEL, new_position)              
                            log.info("Turning right > Old position " + str(current_position) + ", New position " + str(new_position))

                        #else:
                        #    print("X on target")

                        
                        if to_move[1] == -1:        # target_y_status = -1, target < center

                            current_position = psc.get_servo_position(SERVO_Y_CHANNEL) 
                            new_position = current_position - POSITION_FACTOR_Y
                            psc.set_servo_position(SERVO_Y_CHANNEL, new_position)  
                            log.info("Turning up > Old position " + str(current_position) + ", New position " + str(new_position))
                                     
                        
                        elif to_move[1] == 1:         # target_y_status = 1, center < target 

                            current_position = psc.get_servo_position(SERVO_Y_CHANNEL) 
                            new_position = current_position + POSITION_FACTOR_Y
                            psc.set_servo_position(SERVO_Y_CHANNEL, new_position)  
                            log.info("Turning down > Old position " + str(current_position) + ", New position " + str(new_position))
                             
                        #else:
                        #    print("X on target")
                

                ''' FOLLOW MODE '''
                if PSC_PLATFORM_ENABLED:
                    
                    # check if target is within a subset of the frame
                    if in_range( (frame.shape[1], frame.shape[0]), target):
                        
                        ''' If target is in front (large countour size), send command to PSC to STOP rotation  '''
                        ''' Else if target in in sight, move towards (follow state) it '''
                        
                        if state != "stopped" and largest_contour.size >= 900:
                            print("Target in front, setting state to stopped")
                            log.info("Reached target, stopping")
                            rotate_servo(1, "idle")
                            rotate_servo(2, "idle")
                            rotate_servo(3, "idle")
                            rotate_servo(4, "idle")  
                            state = "stopped"

                        elif state != "following" and 100 < largest_contour.size and largest_contour.size < 900: 
                            log.info("Object in distance (contour size " + str(largest_contour.size) + "), moving")
                            print("Target in distant sight, setting state to following")
                            rotate_servo(1, "idle")            
                            rotate_servo(2, "clockwise")
                            rotate_servo(3, "idle")
                            rotate_servo(4, "counter_clockwise")
                            state = "following"

                        else:
                            print("Target in sight, current state = " + state + ", contour size = " + str(largest_contour.size))

            
            else:
                ''' TARGET NOT IN SIGHT '''

                ''' FOLLOW MODE : Send command to PSC to rotate hoping to find contour of target '''
                if PSC_PLATFORM_ENABLED:

                    if state != "rotating":

                        print("Target NOT in sight, setting state to rotating")
                        rotate_servo(1, "clockwise")
                        rotate_servo(2, "clockwise")
                        rotate_servo(3, "clockwise")
                        rotate_servo(4, "clockwise")
                        state = "rotating"

                        
                    else:
                        print("Target NOT in sight, current state = " + state)

                        
            # show the drawing
            #if UI_ENABLED:
            cv2.imshow('frame', frame)

            # check for escape to quit or shared_mem

            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
            if shared_mem[app_name] == "STOP":
                break

            # adding sleep improves servo control, but severely impacts opencv and camera
            #time.sleep(0.5)


        psc.set_default_positions()
        cv2.destroyAllWindows()
        log.info("Goodbye")
        thread.exit()
    
    except Exception, e:
        msg = "Unhandled exception in '" + app_name + "', exiting thread \n" + traceback.format_exc()
        log.error(msg)
        thread.exit()



def in_range(frame_size, target):
    ''' Determines if target coordinates fall within in a subset of screen '''
    enter = time.time()
    # threshold defines whether target coordinated (in a 
    # particular dimension) is within range, in pixels
    threshold_x = 175
    threshold_y = 135
        
    center_x = frame_size[0]/2
    center_y = frame_size[1]/2

    # check if x coord fall within range
    if target[0] < (center_x - threshold_x) or (center_x + threshold_x) < target[0]:
        return False
    
    if target[1] < (center_y - threshold_y) or (center_y + threshold_y) < target[1]:
        return False
    
    # both x and y checks pass
    exit = time.time()
    print("in_range() took " + str(exit-enter))
    return True



def get_next_move(frame_size, target):
    ''' Given a target point on screen, returns direction to move in to hit target '''
    ''' Note: traget param (tuple of x,y coordinates) is the target object, NOT center of image/frame '''
    ''' Returns a tuple with direction values for x and y ... '''
    ''' TODO Refactor to use in_range() function '''
    # TODO Refactor enum/ints into constants:
    # -1 = Move left or up (towards origin)
    #  0 = On target
    #  1 = Move right or down (towards H,W)
    enter = time.time()
    log_msg =  "get_next_move() frame_size = " + str(frame_size)
    log_msg += ", target object = " + str(target)
    
    # threshold defines whether targer coordinated (in a 
    # particular dimension) is within range, in pixels
    threshold_x = 175
    threshold_y = 135
        
    center_x = frame_size[0]/2
    center_y = frame_size[1]/2

    log_msg += ", threshold_x = " + str(threshold_x)
    log_msg += ", threshold_y = " + str(threshold_y)
    #print(log_msg)
    #print(" > center_x = " + str(center_x))
    #print(" > center_y = " + str(center_y))

    # check x coord, assume on track
    target_x_status = 0
    if target[0] < (center_x - threshold_x):
    #    print("Look left")
        target_x_status = -1

    elif (center_x + threshold_x) < target[0]:
    #    print("Look Right")
        target_x_status = 1
    #else:
    #    print("X on target")

    # check y coord, assume on track
    target_y_status = 0
    if target[1] < (center_y - threshold_y):
    #    print("Look Up")
        target_y_status = -1

    elif (center_y + threshold_y) < target[1]:
    #    print("Look Down")
        target_y_status = 1
    #else:
    #    print("Y on target")

    # decide next move based on above
    exit = time.time()
    print("next_move() took " + str(exit-enter) )
    return (target_x_status, target_y_status) #"Unknown"
   
