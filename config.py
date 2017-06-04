
import logging

settings = {        
    'logging_level': logging.WARN, 
    'flask_debug' : True,
    'http' : {
        'host' : "0.0.0.0",
        'port' : 80
    }, 
    'servo_setup' : [
       {
        'manufacturer' : 'Parallax',
        'model' : '900-00008',
        'id' : '',
        'channel' : 1,
        'continuous_rotation' : True,
        'calibration' :
            {
             'clockwise' : 742,
             'idle' : 772,  # DO NOT CHANGE
             'counter_clockwise' : 802
            }
        },
       {
        'manufacturer' : 'Parallax',
        'model' : '900-00008',
        'id' : '',
        'channel' : 2,
        'continuous_rotation' : True,
        'calibration' : {
             'clockwise' : 736,
             'idle' : 766,  # DO NOT CHANGE
             'counter_clockwise' : 796
             }
        },
       {
        'manufacturer' : 'Parallax',
        'model' : '900-00008',
        'id' : '',
        'channel' : 3,
        'continuous_rotation' : True,
        'calibration' : {
             'clockwise' : 736,
             'idle' : 766,  # DO NOT CHANGE
             'counter_clockwise' : 796
             }
        },
       {
        'manufacturer' : 'Parallax',
        'model' : '900-00008',
        'id' : '',
        'channel' : 4,
        'continuous_rotation' : True,
        'calibration' : {
             'clockwise' : 736,
             'idle' : 766,  # DO NOT CHANGE
             'counter_clockwise' : 796
             }
        },

        # NON continuous rotation        
        {
        'manufacturer' : 'HiTech',
        'model' : 'HS-225MG',
        'id' : '',
        'channel' : 15,
        'continuous_rotation' : False,
        'calibration' : {
             'min' : 300,
             'default' : 750,
             'max' : 1200
         }  
        },
        {
        'manufacturer' : 'HiTech',
        'model' : 'HS-645MG',
        'id' : '',
        'channel' : 14,
        'continuous_rotation' : False,
        'calibration' : {
             'min' : 300,
             'default' : 750,
             'max' : 1200
         }
        }                                                                    
   ],
   'web_cam_device_id' : 0
}
