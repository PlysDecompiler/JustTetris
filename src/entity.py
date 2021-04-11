#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import random

from PySide2.QtCore import QRect
from PySide2.QtGui import QFont

from src.opengl import *
from src.constants import Colors
from src.world import Entity


Tetriminos = [
    # T (purple)
    [[0, 1, 0],
     [1, 1, 1]],
    # S (green)
    [[0, 2, 2],
     [2, 2, 0]],
    # Z (red)
    [[3, 3, 0],
     [0, 3, 3]],
    # J (blue)
    [[4, 0, 0],
     [4, 4, 4]],
    # L (orange)
    [[0, 0, 5],
     [5, 5, 5]],
    # I (cyan)
    [[6, 6, 6, 6]],
    # O (yellow)
    [[7, 7],
     [7, 7]]
]
# second piece in the bottom row is the rotation anchor

Config = {
    'cols': 10,
    'rows': 20
}


class Drawer(object):
    def __init__(self):
        super(Drawer, self).__init__()

    @staticmethod
    def draw_line_rectangle(x1, y1, x2, y2):
        glBegin(GL_LINE_LOOP)
        glVertex2d(x1, y1)
        glVertex2d(x2, y1)
        glVertex2d(x2, y2)
        glVertex2d(x1, y2)
        glEnd()

    @staticmethod
    def draw_filled_rectangle(x1, y1, x2, y2):
        glBegin(GL_QUADS)
        glVertex2d(x1, y1)
        glVertex2d(x2, y1)
        glVertex2d(x2, y2)
        glVertex2d(x1, y2)
        glEnd()


class MenuItem(Entity):
    area: QRect

    def __init__(self, text, area: QRect, game):
        super(MenuItem, self).__init__()
        # self.clickable = None
        self.text = text
        self.area = area
        self.game = game
        self.scene = None  # just initializing, assignment happens where entity is created

    def set_area(self, rect):
        self.area = rect

    def set_action(self, action):
        self.programmedAction = action
        # later make it add action, or should there be a dict for clickable -> action,
        # or should this sorting rather happen in some other place

    def set_clickable(self, rect):
        self.clickable = rect
        # put a QRect in as the clickable field

    def draw_line_rectangle(self, x1, y1, x2, y2):
        glBegin(GL_LINE_LOOP)
        glVertex2d(x1, y1)
        glVertex2d(x2, y1)
        glVertex2d(x2, y2)
        glVertex2d(x1, y2)
        glEnd()

    def draw_filled_rectangle(self, x1, y1, x2, y2):
        glBegin(GL_QUADS)
        glVertex2d(x1, y1)
        glVertex2d(x2, y1)
        glVertex2d(x2, y2)
        glVertex2d(x1, y2)
        glEnd()

    def draw_main(self, viewport):
        glLoadIdentity()
        glScale(0.01, 0.01, 0.01)

        glLineWidth(2)
        glColor3ub(244, 200, 100)
        self.draw_line_rectangle(float(self.area.left()), float(self.area.bottom()),
                                 float(self.area.right()), float(self.area.top()))
        glLineWidth(1)

        fnt: QFont = self.scene.font
        fnt.setPointSizeF(20.0)
        viewport.renderText(
            float(self.area.left() + 0.3 * self.area.width()), float(self.area.top() + 0.3 * self.area.height()), -1., self.text, fnt
        )
        

class DeliveryItem(Entity):
    def __init__(self, pos, content):
        super(DeliveryItem, self).__init__()
        self.radius = 5
        self.pos = pos
        self.scene = None  # just initializing, assignment happens where entity is created
        self.content = content
        # instead of circles or ellipses I could try rhombus

        # for now only make numbers that one has to get in ascending order

    def draw_main(self, viewport):
        glLoadIdentity()
        glScale(0.01, 0.01, 0.01)

        greyTone = 44

        glLineWidth(2)
        glColor3ub(244, greyTone, greyTone)
        glBegin(GL_LINE_LOOP)
        for i in range(18):
            radang = math.radians(i*20)
            glVertex2d(self.pos[0]+math.cos(radang)*self.radius, self.pos[1]+math.sin(radang)*self.radius)
        # drawCircle
        glEnd()
        glLineWidth(1)

        fnt: QFont = self.scene.font
        fnt.setPointSizeF(20.0)

        glColor3ub(0, 255, 255)
        viewport.renderText(
            float(self.pos[0]), float(self.pos[1]), -1., self.content.strip(), fnt
        )


# Train or Snake? Maybe allow both with a setting
class TronTrain(Entity):
    def __init__(self, pos):
        super(TronTrain, self).__init__()

        self.scene = None  # just initializing, assignment happens where entity is created
        self.pos = pos
        self.direction = [0, 1]  # use an angle here for continuous direction
        self.angle = 90
        self.speed = 0.4
        self.maxSpeed = 10
        self.minSpeed = 0.1
        self.posHistory = [(pos[0], pos[1]-3), pos]
        self.health = 100
        self.trainLen = 40  # should start lower, should rise with more caught things
        # maybe I can use the same variable for continuous and discrete, I just have to make a transformation inbetween

    def accelerate(self):
        if self.speed <= self.maxSpeed:
            self.speed += 0.1

    def brake(self):
        if self.speed > self.minSpeed:
            self.speed -= 0.1

    def turn(self, da):
        self.angle += da

    def lose_health(self, amount):
        if self.health >= amount:
            self.health -= amount

    def regenerate_health(self, amount):
        if self.health + amount <= 100:
            self.health += amount

    def jump(self):
        pass
        # maybe just throw the next movement also into a different array so that it can be known as not part of the line

    def move(self):
        movement = (self.speed * math.cos(math.radians(self.angle)), self.speed * math.sin(math.radians(self.angle)))
        self.pos = (self.pos[0]+movement[0], self.pos[1]+movement[1])
        self.posHistory.append(self.pos)

    def draw_main(self, viewport):
        glLoadIdentity()
        glScale(0.01, 0.01, 0.01)

        glLineWidth(3)
        glBegin(GL_LINE_STRIP)
        # for posIndex in range(len(self.posHistory)-1, -1, -2)[:10]:
        for posIndex in range(len(self.posHistory) - 1, -1, -1)[:self.trainLen]:
            if posIndex >= 0 and posIndex - 1 >= 0:
                glColor3ub(0, int(250-(250/self.trainLen)*(len(self.posHistory)-posIndex)), 0)
                glVertex2d(*self.posHistory[posIndex])
                # glVertex2d(*self.posHistory[posIndex-1])
        glEnd()

        glLineWidth(1)

        glColor3ub(255,255,255)
        changeY = 3
        Drawer.draw_line_rectangle(-80, -80 + changeY, -80 + 20, -80 + 2 + changeY)
        glColor3ub(int(255-255/100.*self.health), int(0+255/100.*self.health), 0)
        Drawer.draw_filled_rectangle(-80, -80 + changeY, -80 + 20*self.health/100., -80 + 2 + changeY)

        viewport.renderText(-80., -85., -1.,
                            f"Health: {self.health}/100",
                            self.scene.font)
        try:
            if self.scene.game.lastTrainHit:
                viewport.renderText(-80., -60., -1.,
                                "Next Word: " + str(self.scene.game.lastTrainHit),
                                self.scene.font)
        except Exception as e:
            print(e)


class Stone(Entity):
    def __init__(self, trio, pos, kind):
        super(Stone, self).__init__()
        self.pos = pos
        self.kind = kind
        self.trio = trio
        self.onField = True


class Tetrimino(Entity):
    def __init__(self, field, kind, startPos):
        super(Tetrimino, self).__init__()
        self.field = field
        self.kind = kind
        self.pos = startPos
        self.alive = True
        self.mainStone = None
        self.stones = []
        # self.preview = True

    def die(self):
        self.alive = False
        # print(self.field.scene.game.gameName)
        # self.field.check_for_game_over()
        self.field.check_for_completions()
        self.field.spawn_tetrimino()
        # spawn_tetrimino checks for gameover because it checks whether spawning actually works

    # rotate clockwise around the mainStone
    # maybe filter the rotation of O?
    def rotate(self):
        transFormDict = {}
        originalPositionDict = {}
        for stone in self.stones:
            if stone == self.mainStone:
                continue
            mainDiff = (stone.pos[0] - self.mainStone.pos[0], stone.pos[1] - self.mainStone.pos[1])
            newMainDiff = (mainDiff[1], -mainDiff[0])
            newPos = (self.mainStone.pos[0] + newMainDiff[0], self.mainStone.pos[1] + newMainDiff[1])
            transFormDict[stone.pos] = newPos
            originalPositionDict[stone.pos] = stone

            if newPos[1] < 0 or not 0 <= newPos[0] < Config['cols']:
                return

            content = self.field.playArea[newPos]
            if type(content) == Stone and content not in self.stones:
                return

        for stone in self.stones:
            # need to be careful not to overwrite one of those stones right away
            if stone.pos in transFormDict:
                newPos = transFormDict[stone.pos]
                self.field.playArea[newPos] = originalPositionDict[stone.pos]
                if stone.pos not in transFormDict.values():
                    self.field.playArea[stone.pos] = None
                stone.pos = newPos


    def fall(self, checkForCollision, crash=False):
        # maybe I don't have to check for collision in game.py because I can do it here?
        if checkForCollision:
            # if not self.field.scene.game.gameOn:
            #     print("shouldn't work")
            if self.alive and self.field.scene.game.gameOn:
                restHeight = Config['rows']
                fallRange = list(range(1, restHeight)) if crash else [1]
                for fallDepth in fallRange:
                    # the inner part worked for 1-fall already, but does this simple loop
                    # allow for crashing down?
                    for stone in self.stones:
                        newPos = (stone.pos[0], stone.pos[1] - 1)
                        if newPos[1] <= -1:
                            self.die()
                            return

                        content = self.field.playArea[newPos]
                        if type(content) == Stone and content not in self.stones:
                            self.die()
                            return

                    for stone in sorted(self.stones, key=lambda st: st.pos[1]):  # sort by lowness
                        newPos = (stone.pos[0], stone.pos[1]-1)
                        self.field.playArea[newPos] = self.field.playArea[stone.pos]
                        self.field.playArea[stone.pos] = None
                        stone.pos = newPos
        else:
            print('I just died')
            self.die()

    # make tetrimino fall all the way down, also show a block shadow where it would land at any time, with a setting
    def crash_down(self):
        self.fall(True, True)

    def move_down(self):
        self.fall(True)

    def move_left(self):
        for stone in self.stones:
            newPos = (stone.pos[0] - 1, stone.pos[1])
            if newPos[0] <= -1:
                return

            content = self.field.playArea[newPos]
            if type(content) == Stone and content not in self.stones:
                return

        for stone in sorted(self.stones, key=lambda st: st.pos[0]):
            newPos = (stone.pos[0]-1, stone.pos[1])
            self.field.playArea[newPos] = self.field.playArea[stone.pos]
            self.field.playArea[stone.pos] = None
            stone.pos = newPos

    def move_right(self):
        for stone in self.stones:
            newPos = (stone.pos[0] + 1, stone.pos[1])
            if newPos[0] >= Config['cols']:
                return

            content = self.field.playArea[newPos]
            if type(content) == Stone and content not in self.stones:
                return

        for stone in sorted(self.stones, key=lambda st: st.pos[0], reverse=True):
            newPos = (stone.pos[0] + 1, stone.pos[1])
            self.field.playArea[newPos] = self.field.playArea[stone.pos]
            self.field.playArea[stone.pos] = None
            stone.pos = newPos

    def build_self(self):
        pattern = Tetriminos[self.kind-1]
        stoneFits = True
        # iterate over pattern to see if it fits and append stones to tetrimino
        for j, y in enumerate(pattern):
            for i, x in enumerate(pattern[j]):
                if pattern[j][i]:
                    pos = (self.pos[0]+i, self.pos[1]-j)
                    stone = self.spawn_stone(pos)
                    if j == len(pattern) - 1 and i == 1:
                        self.mainStone = stone

                    if self.field.playArea[pos] is not None:
                        stoneFits = False
                        break
            else:
                continue
            break
        if stoneFits:
            # iterate over stones
            for newStone in self.stones:
                self.field.playArea[newStone.pos] = newStone
        else:
            print("Game OVER")
            self.field.scene.game.gameOn = False
            self.field.scene.game.back_to_start_menu()

    def spawn_stone(self, pos):
        newStone = Stone(self, pos, self.kind)
        self.stones.append(newStone)
        return newStone


class Field(Entity):
    def __init__(self):
        super(Field, self).__init__()

        self.scene = None  # just initializing, assignment happens where entity is created
        self.cols = Config['cols']
        self.rows = Config['rows']
        self.currentTetri = None
        self.playArea = {(x, y): None for x in range(self.cols) for y in range(self.rows+3)}
        self.nextKind = random.randint(1,7)
        self.spawn_tetrimino()

        # holds the stashed tetrimino if there is one
        self.stash = None
        # holds the coordinates of the stashed tetrimino and saves the stones
        self.stashed = {}

    def spawn_tetrimino(self):
        newTetri = Tetrimino(self, self.nextKind, (3, self.rows))
        newTetri.build_self()
        self.nextKind = random.randint(1, 7)
        self.currentTetri = newTetri

    def check_for_completions(self):
        eliminateRows = []
        for y in range(self.rows):
            if not any([self.playArea[(x, y)] is None for x in range(self.cols)]):
                eliminateRows.append(y)

        if len(eliminateRows) > 0:
            self.scene.game.combo += 1
            self.scene.game.newPoints = len(eliminateRows)**2*self.scene.game.combo
            self.scene.game.fallSpeedTrigger += self.scene.game.newPoints
            self.scene.game.gamePoints += self.scene.game.newPoints
            self.scene.game.newPointsTimer = 0
            if self.scene.game.fallSpeedTrigger > 6:
                if self.scene.game.fallSpeed >= 3:
                    self.scene.game.fallSpeed -= 2
                    self.scene.game.fallSpeedTrigger = 0
        else:
            self.scene.game.combo = 0

        self.eliminate_rows(eliminateRows)

    # maybe I just have to check whether I can spawn a new stone while I spawn a new stone, if
    # not it's automatically game over
    # def check_for_game_over(self):
    #     for x in range(self.cols):
    #         for y in range()

    def eliminate_rows(self, rows):
        for row in reversed(rows):
            for x in range(self.cols):
                del self.playArea[(x,row)]
                self.playArea[(x,row)] = None
            for y in range(row+1, self.rows):
                for x in range(self.cols):
                    stone = self.playArea[(x,y)]
                    newPos = (x, y-1)
                    self.playArea[(x,y)] = None
                    if type(stone) == Stone:
                        stone.pos = newPos
                        self.playArea[newPos] = stone

    # drop the current
    def drop_down(self):
        self.currentTetri.crash_down()
        # look at the move down function and move down as far as possible

    def swap_stash(self):
        if self.stash is not None:
            stashedMainStone = self.stash.mainStone
            currentMainStone = self.currentTetri.mainStone

            loadedTetri = Tetrimino(self, self.stash.kind, currentMainStone)

            newPositions = {
                stone.pos: (
                    stone.pos[0] - stashedMainStone.pos[0] + currentMainStone.pos[0],
                    stone.pos[1] - stashedMainStone.pos[1] + currentMainStone.pos[1],
                )
                for stone in self.stash.stones
            }

            for key in newPositions:
                newStone = Stone(loadedTetri, currentMainStone, loadedTetri.kind)
                newStone.pos = newPositions[key]
                if newPositions[key] == currentMainStone.pos:
                    loadedTetri.mainStone = newStone
                loadedTetri.stones.append(newStone)

            # check for possible collisions when returning from stash
            for key in newPositions.keys():
                if newPositions[key] not in self.playArea:
                    return
                possibleCollision = self.playArea[newPositions[key]]
                if possibleCollision is None:
                    continue
                # the calculated stone-position already exists in the field and is not the stone to be stashed
                if self.playArea[possibleCollision.pos] not in self.currentTetri.stones:
                    return

            # free fields occupied by current field
            for stone in self.currentTetri.stones:
                self.playArea[stone.pos] = None

            # set new stuff in playArea with items from temp
            for stone in loadedTetri.stones:
                self.playArea[stone.pos] = stone

            # swap stash with current
            self.currentTetri.alive = False
            self.stash.alive = False

            self.stash = self.currentTetri
            self.currentTetri = loadedTetri
            self.currentTetri.alive = True

        else:
            for stone in self.currentTetri.stones:
                self.playArea[stone.pos] = None

            self.currentTetri.alive = False
            self.stash = self.currentTetri

            self.spawn_tetrimino()

    def rotate(self):
        self.currentTetri.rotate()

    def move_left(self):
        self.currentTetri.move_left()

    def move_right(self):
        self.currentTetri.move_right()

    def move_down(self):
        self.currentTetri.move_down()

    def draw_line_rectangle(self, x1, y1, x2, y2):
        glBegin(GL_LINE_LOOP)
        glVertex2d(x1, y1)
        glVertex2d(x2, y1)
        glVertex2d(x2, y2)
        glVertex2d(x1, y2)
        glEnd()

    def draw_filled_rectangle(self, x1, y1, x2, y2):
        glBegin(GL_QUADS)
        glVertex2d(x1, y1)
        glVertex2d(x2, y1)
        glVertex2d(x2, y2)
        glVertex2d(x1, y2)
        glEnd()

    def draw_main(self, viewport):
        if self.scene.game.gameOn:
            glLoadIdentity()
            glScale(0.01, 0.01, 0.01)

            size = 8
            left = -80
            right = left + self.cols*size
            bottom = -80
            top = bottom + self.rows*size
            margin = 0.5
            greyTone = 44
            SMALLFONTSIZE = 8
            BIGFONTSIZE = 18

            # full game field:
            glLineWidth(2)
            glColor3ub(244, greyTone, greyTone)
            self.draw_line_rectangle(left, bottom, left+self.cols*size, bottom + self.rows * size)
            glLineWidth(1)

            fnt: QFont = self.scene.font
            fnt.setPointSizeF(BIGFONTSIZE)

            # stash field:
            glColor3ub(greyTone, 255, greyTone)
            viewport.renderText(
                float(right + 1 * size), float(bottom + (self.rows - 7.5) * size), -1., "Stash (shift):", fnt
            )
            # TODO: how about some rotating color effect on the edge
            glColor3ub(greyTone, greyTone, greyTone)
            self.draw_line_rectangle(right + 1 * size, bottom + (self.rows-13) * size,
                                     right + 6 * size, bottom + (self.rows-8) * size)

            if self.stash is not None:
                mainStone: Stone = self.stash.mainStone
                stashMiddle = (right + 3.5 * size, top - 10.5*size)
                midmargin = 0.5*size-margin
                glColor3ub(*Colors.all()[mainStone.kind])
                for stone in self.stash.stones:
                    newPos = ((stone.pos[0]-mainStone.pos[0])*size+stashMiddle[0],
                              (stone.pos[1]-mainStone.pos[1])*size+stashMiddle[1])
                    self.draw_filled_rectangle(
                        newPos[0]-midmargin, newPos[1]-midmargin,
                        newPos[0]+midmargin, newPos[1]+midmargin,
                    )
            fnt.setPointSizeF(SMALLFONTSIZE)
            glColor3ub(127, 127, greyTone)
            viewport.renderText(
                float(right + 1 * size), float(bottom + (self.rows - 14.4) * size),
                -1., "Press p for pause.", fnt
            )
            glColor3ub(127, 127, greyTone)
            viewport.renderText(
                float(right + 1 * size), float(bottom + (self.rows - 15.0) * size),
                -1., "Press q for quality. (only works with certain gamemodes and with certain tetriminos)", fnt
            )
            glColor3ub(127, 127, greyTone)
            viewport.renderText(
                float(right + 1 * size), float(bottom + (self.rows - 15.6) * size),
                -1., "Press k to toggle debug mode", fnt
            )

            fnt.setPointSizeF(BIGFONTSIZE)
            gt = self.scene.game.newPointsTimer
            if self.scene.game.newPoints > 0 and self.scene.game.combo > 0:
                glColor3ub(int(25*(10-gt)), int(25*(10-gt)), greyTone)
                viewport.renderText(
                    float(right + 1 * size) + gt, float(bottom + (self.rows - 17) * size),
                    -1., "+" + str(self.scene.game.combo) + ' * ' + str(self.scene.game.newPoints//self.scene.game.combo), fnt
                )

            glColor3ub(255, 255, greyTone)
            viewport.renderText(
                float(right + 1 * size), float(bottom + (self.rows - 18) * size),
                -1., "Points: " + str(self.scene.game.gamePoints), fnt
            )

            glColor3ub(255, 255, greyTone)
            viewport.renderText(
                float(right + 1 * size), float(bottom + (self.rows - 19) * size),
                -1., "Combo: " + str(self.scene.game.combo), fnt
            )

            # next tetrimino field:
            glColor3ub(greyTone, 225, greyTone)
            viewport.renderText(
                float(right + 1 * size), float(bottom + (self.rows - 0.5) * size), -1., "Next:", fnt
            )
            glColor3ub(greyTone, greyTone, greyTone)
            self.draw_line_rectangle(right + 1 * size, bottom + (self.rows - 6) * size,
                                     right + 6 * size, bottom + (self.rows - 1) * size)

            colorNum = self.nextKind
            for y, row in enumerate(Tetriminos[colorNum-1]):
                for x, col in enumerate(row):
                    glColor3ub(*Colors.all()[colorNum])
                    if col != 0:
                        self.draw_filled_rectangle(
                            right + (x + 2) * size + margin, top - (y + 4) * size + margin,
                            right + (x + 3) * size - margin, top - (y + 3) * size - margin,
                        )
            fnt.setPointSizeF(10.0)
            for ic in range(self.cols):
                for ir in range(self.rows):
                    stone = self.playArea[(ic, ir)]

                    if stone is not None:

                        # assert(Stone == type(kind))
                        colorNum = stone.kind

                        glColor3ub(*Colors.all()[colorNum])
                        self.draw_filled_rectangle(
                            left + ic*size + margin,  bottom + ir*size + margin,
                            left + (ic+1)*size - margin, bottom + (ir+1)*size - margin
                        )

                        # JUST FOR DEBUGGING show the mainStone
                        if self.scene.debugMode and stone.trio.mainStone == stone:
                            glBegin(GL_LINES)
                            glColor3ub(255, 255, 255)
                            glVertex2d(left + ic * size + margin, bottom + ir * size + margin)
                            glVertex2d(left + (ic + 1) * size - margin, bottom + (ir + 1) * size - margin)
                            glEnd()
                        # show the currently alive stone if debug mode is on
                        if self.scene.debugMode and stone.trio.alive:
                            glPointSize(5)
                            glBegin(GL_POINTS)
                            glColor3ub(255, 0, 255)
                            glVertex2d(left + ic * size + 0.5*size, bottom + ir * size + 0.5*size)
                            # glVertex2d(left + (ic + 1) * size - margin, bottom + (ir + 1) * size - margin)
                            glEnd()
                            glPointSize(1)
                    # content of every field
                    if self.scene.debugMode:
                        glColor3ub(150, 150, 150)
                        viewport.renderText(float(left + ic*size), float(bottom + ir*size), -1.,
                                            "None" if stone is None else str(stone.kind), fnt)

