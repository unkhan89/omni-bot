
import sys
import time
import traceback
import serial 
from serial.tools import list_ports

'''
This class abstracts Parallax Propeller Servo Controller
A servo 'channel' within this class denotes a single port on
the PSC hardware to which a servo is connected.

'''

class PSC:
    
    log = None
    dev = None  # serial device
    DEVICE_ID = 'USB VID:PID=0403:6001 SNR=A4004Ee9'
    my_port = None
    timeout = 1.5 
    baudrate = 2400
    ramp_speed = 10
    
    COMMAND_SET_POSITION = "!SC" # + <channel> + <ramp speed=15> + <lowbyte=position> + <highbyte=position>>8> + <CR> 
    COMMAND_GET_POSITION = "!SCRSP" # + <channel> + <CR>
    RETURN_CARRIAGE = "\r"

    servo_setup = None # dictionary that holds info about physical setup of servos
    
    
    
    def __init__(self, logger, servo_setup_param):
        
        try:
            
            if logger is None :
                raise Exception("No logger provided")
            
            self.log = logger
            self.log.debug("Initializing Paralllax Servo Controller")        
        
            if servo_setup_param is None or len(servo_setup_param) == 0:
                self.log.warn("No servo setup info given")
            else:
                
                # validate given servo_setup 
                for temp_serv in servo_setup_param:
                    if (
                        not temp_serv.has_key('continuous_rotation') or 
                        not temp_serv.has_key('channel') or
                        not temp_serv.has_key('calibration')
                        ):
                        raise Exception("Bad servo setup provided")

                    if temp_serv['continuous_rotation'] == True:
                        if (
                            not temp_serv['calibration'].has_key('clockwise') or
                            not temp_serv['calibration'].has_key('idle') or
                            not temp_serv['calibration'].has_key('counter_clockwise')
                            ):
                            raise Exception("Bad servo setup provided") 
                    else:
                        if(
                            not temp_serv['calibration'].has_key('min') or
                            not temp_serv['calibration'].has_key('default') or
                            not temp_serv['calibration'].has_key('max')                            
                            ):
                            raise Exception("Bad servo setup provied")   
                
                # setup is good
                self.servo_setup = servo_setup_param 
            
            # find PSC usb device
            for index, port in enumerate(list_ports.comports()):            
                self.log.debug("Port " +  str(index) + ": " + str(port))
                if port[2] == self.DEVICE_ID:
                    my_port = port
                    break

            # check if device was found
            if my_port is None:
                self.log.error("my_port is None")
                raise Exception("Unable to find device! Port is null")
            
            # log PSC info
            self.log.info("Parallax servo board found")
            self.log.debug("Port: " + my_port[0])
            self.log.debug("About: " + my_port[1])
            self.log.debug("Hardware: " + my_port[2])
            
            # create pyserial object for communicating with PSC usb device
            self.dev = serial.Serial(port=my_port[0], timeout=self.timeout, baudrate=self.baudrate)
            
        
        except Exception, e:
            print("PSC.__init__() Failed to initialize PSC \n" + traceback.format_exc() )
            
        
    def is_device_ready(self):
        return self.dev.isOpen()
    
    
    def close_device(self):
        self.dev.close()    
        

    def set_default_positions(self):
        ''' Sets all servos in servo_setup to their default/idle positions '''
        self.log.info("Setting all servos to default positions")
        for servo in self.servo_setup:
            if servo['continuous_rotation'] == True:
                self.set_servo_position(servo['channel'], servo['calibration']['idle'])
            else:
                self.set_servo_position(servo['channel'], servo['calibration']['default'])

    # TODO 
    def set_baud_rate(self):
        self.log.info("Attempting to set baud rade")
            # !SCSBR <mode> <CR>
        try:        
            command_bytes = bytearray("!SCSBR", "utf-8")
            command_bytes.append(1) # mode
            carriage_return_bytearray = bytearray(self.RETURN_CARRIAGE, "utf-8")
            command_bytes.append(carriage_return_bytearray[0])
            
            #self.log.debug("Sending command: " + command_bytes)
            self.write(command_bytes)
            
#             time.sleep(1) # why is this here?
#             
#             #self.log.debug("Reading response")
#             response = self.read(3)
#             #self.log.debug("response  = " + response)
#             
#             for byte in response:
#                 #self.log.debug(" > byte = " + str(byte))
            
            
        except Exception, e:
            self.log.error("PSC.set_baud_rate() \n" + traceback.format_exc() )
            return -1  
    
    
    def get_servo_status(self, channel):
        try:
            ''' Gets the status of servo, such as position'''
        except Exception, e:
            self.log.error("PSC.get_servo_position() \n" + traceback.format_exc() )
            
        
    def get_servo_position(self, channel):
        self.log.debug("get_servo_position(" + str(channel) + ")")

        try:
            command_bytes = bytearray(self.COMMAND_GET_POSITION, "utf-8")
            command_bytes.append(channel)
            carriage_return_bytearray = bytearray(self.RETURN_CARRIAGE, "utf-8")
            command_bytes.append(carriage_return_bytearray[0])
            
            #self.log.debug("Sending command: " + command_bytes)
            self.write(command_bytes)
            
            #time.sleep(1) # why is this here?
            
            position = self.read(3)
            ch = ''.join( [ "%02X " % ord( x ) for x in position[0] ] ).strip()
            high = ''.join( [ "%02X " % ord( x ) for x in position[1] ] ).strip()
            low = ''.join( [ "%02X " % ord( x ) for x in position[2] ] ).strip()
            #self.log.debug("get_servo_position(): ch (hex)= " + ch)
            #self.log.debug("get_servo_position(): high (hex)= " + high)   
            #self.log.debug("get_servo_position(): low (hex)= " + low)     
            #finalCh = str(int(ch, 16))
            
            finalStr = high + low
            finalPos = int(finalStr, 16)
            return finalPos

        except Exception, e:
            self.log.error("PSC.get_servo_position() \n" + traceback.format_exc() )
            return -1         
        

    def set_servo_position(self, channel, position):
        self.log.debug("set_servo_position(" + str(channel) + ", " + str(position) + ")")
        
        # check whether given position is valid for given servo
        # for servo in self.servo_setup:
        #     if servo['channel'] == channel and servo['continuous_rotation'] == False:
        #         if position not in range(servo['calibration']['min'], servo['calibration']['max']+1):
        #             self.log.warn("Invalid servo position given, ignoring")
        #             return

        try:        
            command_bytes = bytearray(self.COMMAND_SET_POSITION, "utf-8")
            command_bytes.append(channel)
            command_bytes.append(self.ramp_speed)
            lowByte = position & 0x00FF
            highByte = (position & 0xFF00) >> 8
            command_bytes.append(lowByte)
            command_bytes.append(highByte)
            carriage_return_bytearray = bytearray(self.RETURN_CARRIAGE, "utf-8")
            command_bytes.append(carriage_return_bytearray[0])
            for i in range(0, len(command_bytes)):
                try:
                    tempStr = str(unichr( command_bytes[i] ))
                except:
                    tempStr = "Unknown"
                self.log.debug(" > Byte " + str(i) + ": " +  str(command_bytes[i]) + ",  val: " + tempStr)
            self.log.debug("final command_bytes = " + command_bytes)
            
            self.log.debug("Sending command = " + str(command_bytes))
            self.write(command_bytes)
            
            time.sleep(1)     # why is this here?
            self.log.debug("Done setting position")

        except:
            self.log.error("PSC.set_servo_position() \n" + traceback.format_exc() )
            raise
        
        
    def rotate_clockwise(self, channel):
        self.log.debug("rotate_clockwise() channel = " + str(channel) )
        if self.is_servo_continuous_rotation(channel) == False:
            self.log.warn("Attempting to rotate non-continuous servo, ignoring")
        else:
            self.set_servo_position(channel, self.get_crs_clockwise_value(channel) )
        
    
    def rotate_counter_clockwise(self, channel):
        self.log.debug("rotate_counter_clockwise() channel = " + str(channel) )        
        if self.is_servo_continuous_rotation(channel) == False:
            self.log.warn("Attempting to rotate non-continuous servo, ignoring")
        else:                
            self.set_servo_position(channel, self.get_crs_counter_clockwise_value(channel))
        
    
    def idle_cr_servo(self, channel):
        self.log.debug("idle_cr_servo() channel = " + str(channel))
        if self.is_servo_continuous_rotation(channel) == False:
            self.log.warn("Attempting to idle non-continuous servo, ignoring")            
        else:
            self.set_servo_position(channel, self.get_crs_idle_value(channel))
    
    
    
    #####################################################################################################

    def write(self, command):    
        self.log.debug("write()")
        try:      
            if self.dev.isOpen == False:
                self.log.debug("Device is closed, opening it")
                self.dev.open()         
            if len(command) > 8 or len(command) == 0:
                raise Exception("Invalid command length: " + len(command) + ", expecting 8")      
            bytesWritten = self.dev.write(command)
        except:
            self.log.error("PSC.write() \n" + traceback.format_exc() )
            raise
  
  
    def read(self, num_of_bytes):    
        self.log.debug("read() num_of_bytes = " + str(num_of_bytes) )
        try:
            bytesRead = self.dev.read(num_of_bytes)
            #self.log.debug("read(): read num_of_bytes = " + str(len(bytesRead)))
            #self.log.debug("read(): type bytesRead = " + str(type(bytesRead)))     
            #self.log.debug("read(): str(bytesRead) = " + str(bytesRead))                  
            return bytesRead
        except:
            self.log.error("PSC.read() \n" + traceback.format_exc() )
            raise   

    def is_servo_continuous_rotation(self, channel):
        for temp_serv in self.servo_setup:
            if temp_serv['channel'] == channel:
                if temp_serv['continuous_rotation']:
                    return True
                else:
                    return False
        
        self.log.warn("PSC.is_servo_continuous_rotation() No data found for servo on channel " + str(channel))
        return None
        
    '''
        Following functions return the calibrated values of continuous rotation servos
     '''
    def get_crs_idle_value(self, channel):
        for temp_serv in self.servo_setup:
            if temp_serv['channel'] == channel:
                return temp_serv['calibration']['idle']
        
        self.log.warn("PSC.get_crs_idle_value() No data found for servo on channel " + str(channel))
        
    def get_crs_clockwise_value(self, channel):
        for temp_serv in self.servo_setup:
            if temp_serv['channel'] == channel:
                return temp_serv['calibration']['clockwise']
        
        self.log.warn("PSC.get_crs_clockwise_value() No data found for servo on channel " + str(channel))
        
    def get_crs_counter_clockwise_value(self, channel):
        for temp_serv in self.servo_setup:
            if temp_serv['channel'] == channel:
                return temp_serv['calibration']['counter_clockwise']
        
        self.log.warn("PSC.get_crs_counter_clockwise_value() No data found for servo on channel " + str(channel))
        