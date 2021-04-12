#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PySide2.QtOpenGL import QGLWidget
# from PySide2.QtGui import QFont
# from PySide2.QtCore import QRect

from src.opengl import *
from src.entity import Field, MenuItem, DeliveryItem


class Viewport(QGLWidget):
    def __init__(self, perspective, parent=None):
        super(Viewport, self).__init__(parent)
        self.perspective = perspective
    
    def initializeGL(self):
        pass

    def resizeGL(self, w, h):
        self.perspective.viewport_resized(w, h)

    def paintGL(self):
        self.perspective.draw(self)
    
            
class MainPerspective(object):
    def __init__(self, scene):
        self.scene = scene
    
    def setup(self):
        glLoadIdentity()
        
    def viewport_resized(self, width, height):
        side = int(min(width, height))
        # glViewport()
        glViewport(int((width - side) / 2), int((height - side) / 2), side, side)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-100, 100, -100, 100, -100.0, 100.0)
        
    def draw(self, viewport):
        self.setup()

        game = self.scene.game

        # scene draw stuff 
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        '''
        if self.scene.debuggingPoint != (0, 0):
            glLoadIdentity()
            glScale(0.01, 0.01, 0.01)
            drawPos = self.scene.collision.mousepos_to_gamepos(self.scene.debuggingPoint)

            glLineWidth(5)
            glColor3ub(0,255,255)
            glBegin(GL_LINES)
            glVertex2d(*(0,0))
            glVertex2d(*drawPos)
            glEnd()
        '''

        for menu in self.scene.iter_instances(MenuItem):
            menu.draw_main(viewport)

        if not self.scene.game.deliveryGameOn and not self.scene.game.gameOn and not self.scene.game.howToOn:
            viewport.renderText(250. - self.scene.game.inactivityTimer % 600, -80., -1.,
                                "Don't you think the title is a bit boring? You seem to have fallen asleep",
                                self.scene.font)

        if hasattr(self.scene, 'field'):
            field: Field = self.scene.field
            field.draw_main(viewport)
        if hasattr(self.scene.game, 'deliveryGameOn') and self.scene.game.deliveryGameOn:
            self.scene.tronTrain.draw_main(viewport)
            # self.scene.tronTrain.health
            # viewport.renderText(-80., 80., -1.,
            #                     "You activated DeliveryTron: Hit the circles in the correct order!",
            #                     self.scene.font)

            for item in self.scene.iter_instances(DeliveryItem):
                item.draw_main(viewport)

            if game.deliveryMode == 'swe':
                helpText = "Hit a word and then its swedish/english translation!"
            else:
                helpText = "You activated DeliveryTron: Hit the circles in the correct order!"
            viewport.renderText(-80., 80., -1.,
                                helpText,
                                self.scene.font)
            if self.scene.tronTrain:
                train = self.scene.tronTrain
                viewport.renderText(-80., 90., -1.,
                                    "Position: " + str([round(train.pos[0], 1), round(train.pos[1], 1)]),
                                    self.scene.font)

        if self.scene.game.howToOn:
            helptext = []
            helptext.append("This is basically a tetris game.")
            helptext.append("You can control the tetriminos with the arrow keys.")
            helptext.append("Up: to turn the tetrimino, Down: to move it down")
            helptext.append("Space: to let tetrimino fall down")
            helptext.append("Escape: to go back to the main menu.")
            helptext.append("")
            helptext.append("To activate the easter egg, you have to ")
            helptext.append("change the game title.")
            helptext.append("This is done by clicking before the first")
            helptext.append("letter and entering letters.")
            helptext.append("You want the game to be called 'not just tetris'")
            helptext.append("When you have the T-Tetrimino rotated so ")
            helptext.append("it really looks like a T, press the Quality-Button")
            helptext.append("Have fun!")

            for i, text in enumerate(helptext):
                viewport.renderText(-80., 80.-10*i, -1.,
                                    text,
                                    self.scene.font
                                    )

        # glColor3ub(255,255,255)
        # viewport.renderText(20., -40., -1., str('\n'.join(str(s.pos)
        # for s in self.scene.field.currentTetri.stones)), self.scene.font)
        # if self.scene.field.stash is not None:
        #     viewport.renderText(20., -50., -1., str('\n'.join(str(s.pos)
        #     for s in self.scene.field.stash.stones)), self.scene.font)
