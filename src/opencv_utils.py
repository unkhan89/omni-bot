'''
This module contains variables and functions for utilizing OpenCV
 
'''

import numpy
import cv2


COLOR_BLUE = {
    'bgr' : (255, 0, 0),
    'lower_bound' : numpy.array([110, 100, 100]),
    'upper_bound' : numpy.array([130, 255, 255])
}

COLOR_GREEN = {
    'bgr' : (0, 255, 0),
    'lower_bound' : numpy.array([50, 100, 100]),
    'upper_bound' : numpy.array([70, 255, 255])
}

COLOR_RED = {
    'bgr' : (0, 0, 255),
    'lower_bound' : numpy.array([0, 100, 100]),
    'upper_bound' : numpy.array([10, 255, 255])
}

COLOR_YELLOW = {
    'lower_bound' : numpy.array([20, 145, 145]),
    'upper_bound' : numpy.array([40, 255, 255])
}

COLOR_ORANGE = {
    'lower_bound' : numpy.array([5, 135, 135]),
    'upper_bound' : numpy.array([25, 255, 255])
}


def get_corner_coordinates(contour_object, return_np_array=False):
    ''' Given a contour_object, returns an array of top_left and bottom_right coordinates '''
    ''' countour_object is an element of contour_list as returned by cv2.findContours() '''
    ''' returned object is a numpy.array which can be supplied to cv2.drawContours() '''
    '''  '''
    top_left = contour_object[0]
    bottom_right = contour_object[ len(contour_object)/2 ]
    return numpy.array([top_left, bottom_right], numpy.int32)