"""
This module contains collision test functions.
Note:
The naming convention used is lowerdimensional and less complex objects are named first.
""" 

import math
from src.constants import IC


# def point_point(x1,y1,x2,y2,dist = 0.001):  # this kind of is circle circle
#    return math.pow(x1-x2,2) + math.pow(y1-y2,2) < math.pow(dist, 2)     # if within circle

class Collision(object):

    def __init__(self):
        # self.gS = 200.
        self.reload_constants()

    def reload_constants(self):
        # m = mouse, g = game
        self.mSx = IC.VIEW[0]
        self.mSy = IC.VIEW[1]

        self.gSy = IC.VIEW[2]
        self.gSx = IC.VIEW[2] * IC.VIEW[0] / IC.VIEW[1]

        self.mS = IC.VIEW[1]
        self.gS = IC.VIEW[2]
        self.scal = 1.0

    @staticmethod
    def point_point(p1, p2, dist=0.001):  # this kind of is circle circle
        # if within circle
        return math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2) < math.pow(dist, 2)

    @staticmethod
    def point_point_alt(p1, p2, vec):
        return math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2) <= math.pow(vec[0], 2) + math.pow(vec[1], 2)

    # how to determine the direction in which the point may/not pass the line
    # the line has to be given in mathematical positive direction, outside is on the right side
    @staticmethod
    def point_line(px1, py1, lx1, ly1, lx2, ly2):
        pass

    @staticmethod
    def line_line(l1x1, l1y1, l1x2, l1y2, l2x1, l2y1, l2x2, l2y2, already_used=0):
        if l2x2 == l2x1:
            if already_used:
                return False
            else:
                return Collision.line_line(l1y1, l1x1, l1y2, l1x2, l2y1, l2x1, l2y2, l2x2, 1)

        n = float(((l1y2 - l1y1) * (l2x2 - l2x1) - (l1x2 - l1x1) * (l2y2 - l2y1)))
        if (n == 0):
            return False

        r = float(((l1x1 - l2x1) * (l2y2 - l2y1) + (l2y1 - l1y1) * (l2x2 - l2x1)) / n)
        s = float((l1x1 - l2x1 + r * (l1x2 - l1x1)) / (l2x2 - l2x1))

        return 0 <= r <= 1 and 0 <= s <= 1

    # TODO:
    @staticmethod
    def line_circle():
        pass

    @staticmethod
    def circle_in_square(pt, sqpt, sqlen, dist):
        # if pt[0]-sqpt[0] ==

        if ((sqpt[0] + sqlen / 2 <= pt[0] or sqpt[0] - sqlen / 2 >= pt[0])
                and (sqpt[1] + sqlen / 2 <= pt[1] or sqpt[1] - sqlen / 2 >= pt[1])):
            return True

        # return math.pow(pt[0]-sq[0], 2) + math.pow(pt[1]-sq[1], 2) <= math.pow(dist, 2)

    def gamepos_to_mousepos(self, pos, playerpos=(0, 0)):
        return [(pos[0] - playerpos[0]) * self.mS / self.gS + self.mS / 2,
                (pos[1] - playerpos[1]) * (-self.mS / self.gS) + self.mS / 2
                ]

    def mousepos_to_gamepos(self, pos, playerpos=(50, 50)):
        return [2*(pos[0] / (self.mSx / self.gSx)-playerpos[0]), 2*(self.gSy - pos[1] / (self.mSy / self.gSy)-playerpos[1])]











