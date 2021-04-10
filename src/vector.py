#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math


def get_vector(a, b):
    if isinstance(a, Vector2D):
        return a
    elif isinstance(b, Vector2D):
        return b
    else:
        raise ValueError("both not a vector")


def get_scalar(a, b):
    if not isinstance(a, Vector2D):     # TODO test for a scalar instead?? probably not...
        return a
    elif not isinstance(b, Vector2D):
        return b
    else:
        raise ValueError("both not a vector")


class Vector2D(object):
    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], Vector2D):
                self.x, self.y = args[0].x, args[0].y       # TODO refactor
            else:
                self.x, self.y = args[0]
        else:
            self.x, self.y = args
                
    def __add__(self, other):
        return Vector2D(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x-other.x, self.y-other.y)
    
    def __mul__(self, other):       # TODO implement vector vector multiplication or use a library 
        vector = get_vector(self, other)
        scalar = get_scalar(self, other)
        return Vector2D(vector.x*scalar, vector.y*scalar)
    
    def __div__(self, other):
        vector = get_vector(self, other)
        scalar = get_scalar(self, other)
        scalar = 1/scalar
        return Vector2D(vector.x*scalar, vector.y*scalar)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normal(self):
        return Vector2D(self.y, -self.x)
    
    def unit(self):
        # returns the unit vector
        return self.__div__(self.length())
    
    def squared_distance(self):
        return self.x**2 + self.y**2
