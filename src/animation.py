#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtCore import Qt
# from src import collision
from src.entity import MenuItem


class Director(object):
    """
    Directs the Actors to act according to some kind of script which may be based on user input.
    The actors are part of the scene and identified as actors by their description in the script.
    Makes the actors execute according to script.    (script interpreter)
    """

    def __init__(self, scene, script):
        self.scene = scene
        self.script = script

        # keys and buttons that shall be able to be pressed continuosly
        self.key_filter = {Qt.Key_Left, Qt.Key_Right, Qt.Key_Down, Qt.Key_Up,
                           Qt.Key_Space, Qt.Key_PageDown, Qt.Key_PageUp}
        self.button_filter = {Qt.LeftButton, Qt.MidButton, Qt.RightButton}

        self.is_down = set()

    def key_down(self, event):
        key = event.key()

        game = self.scene.game
        game.inactivityTimer = 0
        if not game.gameOn and not game.deliveryGameOn:
            if game.secretEditCursor is not None:
                # iterate over all the keys and get_attr
                for character in [chr(code) for code in range(65, 91)]:
                    if len(self.scene.gameName.text) > 20:
                        break
                    if getattr(Qt, 'Key_' + character) == key:
                        # if game.secretEditCursor
                        game.gameCheatText = game.gameCheatText + character.lower()
                        game.secretEditText = game.secretEditText[:game.secretEditCursor] \
                                              + character.lower() + game.secretEditText[
                                                                    game.secretEditCursor:]
                        # if game.secretEditText.endswith('tetris'):
                        game.secretEditCursor += 1
                        self.scene.gameName.text = game.secretEditText

                if Qt.Key_Space == key:
                    game.secretEditText = game.secretEditText[:game.secretEditCursor] \
                                          + ' ' + game.secretEditText[game.secretEditCursor:]
                    game.secretEditCursor += 1
                    self.scene.gameName.text = game.secretEditText

                if Qt.Key_Delete == key:
                    # TODO: maybe show a funny message or an achievement when you want to delete tetris
                    if game.secretEditCursor < len(game.secretEditText) - 6 and game.secretEditText != 'tetris':
                        game.secretEditText = game.secretEditText[:game.secretEditCursor] \
                                              + game.secretEditText[game.secretEditCursor + 1:]
                        self.scene.gameName.text = game.secretEditText

                if Qt.Key_Backspace == key:
                    if game.secretEditCursor > 0:
                        if game.secretEditText != 'tetris':
                            game.secretEditText = game.secretEditText[
                                                  :game.secretEditCursor - 1] \
                                                  + game.secretEditText[
                                                    game.secretEditCursor:]
                            self.scene.gameName.text = game.secretEditText
                            game.secretEditCursor -= 1
                            # game.main_view.updateGL()

            # print(game.secretEditText)

        # make sure game has started
        if game.gameOn:
            if Qt.Key_P == key:
                game.toggle_pause()

            if hasattr(self.scene, 'field'):
                field = self.scene.field
                if Qt.Key_Left == key:
                    field.move_left()
                if Qt.Key_Right == key:
                    field.move_right()
                if Qt.Key_Down == key:
                    field.move_down()
                if Qt.Key_Up == key:
                    field.rotate()
                if Qt.Key_Shift == key:
                    field.swap_stash()
                if self.scene.game.gameName in ('not tetris', 'not just tetris'):
                    if Qt.Key_Q == key:
                        theTetri = self.scene.field.currentTetri
                        if theTetri.kind == 1:
                            # check if mainstone has no other block on top:
                            if self.scene.field.playArea[
                                (theTetri.mainStone.pos[0], theTetri.mainStone.pos[1] + 1)
                            ] is None:
                                # print('block!!')
                                self.scene.game.start_delivery_tron()
        elif hasattr(self.scene.game, 'deliveryGameOn') and self.scene.game.deliveryGameOn:
            train = self.scene.tronTrain
            if Qt.Key_P == key:
                game.toggle_pause()
            if Qt.Key_Left == key:
                train.turn(10)
            if Qt.Key_Right == key:
                train.turn(-10)
            if Qt.Key_Down == key:
                train.brake()
            if Qt.Key_Up == key:
                train.accelerate()
            if Qt.Key_Space == key:
                train.jump()

        if key in self.key_filter:
            self.is_down.add(key)

    def key_up(self, event):
        key = event.key()
        self.is_down.discard(key)

    def mouse_down(self, event):
        button = event.button()

        if button in self.button_filter:
            self.is_down.add(button)

    def mouse_up(self, event):
        button = event.button()
        mousePos = event.pos()
        self.scene.debuggingPoint = (mousePos.x(), mousePos.y())

        inGameMousePos = self.scene.collision.mousepos_to_gamepos((mousePos.x(), mousePos.y()))
        self.scene.game.inactivityTimer = 0
        # self.scene.game.main_view.updateGL()
        # iterate over all entities
        for ent in self.scene.iter_instances(MenuItem):
            if hasattr(ent, 'clickable'):
                # maybe I have to transform the pos
                if ent.clickable.contains(*inGameMousePos):

                    if hasattr(ent, 'programmedAction'):
                        ent.programmedAction(ent)
                        print(ent.text, 'hit')
                        # ent.doWhatYouDoThen()
                    # else:
                    #    self.scene.game.start_game()
                else:
                    pass

        self.is_down.discard(button)

    def mouse_move(self, event):
        mousePos = event.pos()
        # self.scene.debuggingPoint = (mousePos.x(), mousePos.y())
        # inGameMousePos = self.scene.collision.mousepos_to_gamepos((mousePos.x(), mousePos.y()))
        # print(inGameMousePos)

    def animation_step(self):
        game = self.scene.game
        if hasattr(self.scene.game, 'deliveryGameOn') and self.scene.game.deliveryGameOn:
            train = self.scene.tronTrain
            if Qt.Key_Left in self.is_down:
                train.turn(10)
            if Qt.Key_Right in self.is_down:
                train.turn(-10)
            if Qt.Key_Down in self.is_down:
                train.brake()
            if Qt.Key_Up in self.is_down:
                train.accelerate()

        returnvalue = False
        return returnvalue


class Actor(object):
    """
    provides actions, acted out according to Script, directed by the Director.
    
    TODO
    reason about different types of actions, and how they can be "told" by the director
    timing etc.
    """
    pass


class Script(object):
    """
    Describes a set of entities and how they act upon another
    """
    pass
