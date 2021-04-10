#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# important constants
# should make all those constants with cap letters
class IC(object):
    spawnwidth = 900
    neededcollisioncolor = 127 #153
    amountsources = 42
    movefrequency = 1
    pointspawn = 11          # the greater the number the fewer points will come 10
    netwidth = 25
    POINTLIFE = 42
    pointspeed = 0.1
    start_resources = 5000

    VIEW = [10, 10, 100.]


class Colors(object):
    white   = (255, 255, 255)
    black   = (0, 0, 0)
    red     = (255, 0, 0)
    green   = (0, 255, 0)
    blue    = (0, 0, 255)    
    magenta = (255, 0, 255)
    cyan    = (0, 255, 255)
    yellow  = (255, 255, 0)
    grey    = (127, 127, 127)
    orange  = (255, 127, 0)
    purple  = (127, 0, 255)

    @classmethod
    def all(cls):
        return [cls.grey, cls.red, cls.green, cls.blue, cls.magenta, cls.yellow, cls.cyan, cls.orange, cls.white]
