#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import json

from PySide2.QtCore import QTimer, Qt, QRect
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QApplication

from src.view import Viewport, MainPerspective
from src.world import Scene
from src.entity import Field, MenuItem, TronTrain, DeliveryItem
from src.animation import Director
from src.collision import Collision
from src.constants import IC


class Game(QWidget):
    def keyPressEvent(self, event):
        self.director.key_down(event)

    def keyReleaseEvent(self, event):
        self.director.key_up(event)

    def mousePressEvent(self, event):
        self.director.mouse_down(event)

    def mouseReleaseEvent(self, event):
        self.director.mouse_up(event)

    def mouseMoveEvent(self, event):
        self.director.mouse_move(event)

    def __init__(self, theApp, parent=None):
        super(Game, self).__init__(parent)
        self.setWindowTitle("just tetris")

        tempdesktop = QApplication.desktop()

        self.maxWidth = (tempdesktop.screenGeometry().width() / 100) * 100
        self.maxHeight = (tempdesktop.screenGeometry().height() / 100) * 100

        useScreenSize = False
        if useScreenSize:
            self.viewwidth = self.maxHeight  # 1200
            self.viewheight = self.maxHeight  # 800
            if self.viewheight > self.maxWidth:
                self.viewwidth = self.maxWidth
        else:
            self.viewwidth = 900
            self.viewheight = 900

        self.setGeometry(10, 30, int(self.viewwidth), int(self.viewheight))
        IC.VIEW[0:2] = int(self.viewwidth), int(self.viewheight)

        self.setMouseTracking(True)

        self.scene = Scene()
        self.director = Director(self.scene, None)
        self.scene.game = self
        self.scene.app = theApp
        self.scene.collision = Collision()

        self.setFocusPolicy(Qt.StrongFocus)

        self.main_view = Viewport(MainPerspective(self.scene), self)
        self.main_view.setGeometry(2, 2, int(self.viewwidth), int(self.viewheight))
        self.main_view.setMouseTracking(True)
        # self.scene.add(self.main_view, 'main_view')

        self.scene.font = QFont("Monospace", 12)
        # self.scene.font.setStyleHint(QFont.Monospace)
        # self.scene.font.setFixedPitch(True)
        self.scene.font.setRawMode(True)
        # https://www.programcreek.com/python/example/64923/PySide.QtGui.QFont
        self.scene.app.setFont(self.scene.font)
        self.gameOn = False

        self.scene.debuggingPoint = (0, 0)
        self.scene.debugMode = False
        self.actionQueue = {}
        self.clickConnections = []
        self.inactivityTimer = 0
        self.init_menus()
        self.secretEditCursor = None
        self.secretEditText = None
        self.gameCheatText = ""

        self.howToOn = False
        self.deliveryGameOn = False
        self.deliveryTronNum = 1
        self.deliveryMode = 'swe'
        self.lastTrainHit = 0
        self.currentlyHitting = None
        self.selfHitSegments = []
        self.languageDict = {}

        # start timer
        self.scene.time = 0
        self.start_timer()

    def start_secret_edit_cursor(self):
        self.secretEditText = self.scene.gameName.text
        self.secretEditCursor = 0
        self.inactivityTimer = 0
        # print(self.secretEditCursor)

    def init_menus(self):

        try:
            self.destroy_menus()
        except Exception as e:
            print(e)

        self.turn_everything_off()

        gameName = MenuItem("just tetris", QRect(-40, 60, 80, 15), game=self)
        # secret field: x: -20, -16 # y: 53, 62
        gameName.set_clickable(QRect(-22, 58, 7, 13))
        gameName.set_action(lambda menu: menu.game.start_secret_edit_cursor())
        self.scene.add(gameName, 'gameName')

        startGameRect = QRect(-40, 20, 80, 15)
        startGame = MenuItem("start game", startGameRect, game=self)
        startGame.set_clickable(startGameRect)
        startGame.set_action(lambda menu: menu.game.trigger_start_game())
        self.scene.add(startGame)
        self.inactivityTimer = 0

        howToWidgetRect = QRect(-40, -20, 80, 15)
        howToWidget = MenuItem("How To (Spoilers!)", howToWidgetRect, game=self)
        howToWidget.set_clickable(howToWidgetRect)
        howToWidget.set_action(lambda menu: menu.game.trigger_how_to())
        self.scene.add(howToWidget)

        if hasattr(self, 'gamePoints'):
            previousScore = MenuItem("previous score: " + str(self.gamePoints), QRect(-40, -60, 80, 15), game=self)
            self.scene.add(previousScore, 'previousScore')

    def trigger_start_game(self):
        self.trigger(self.start_game)

    def trigger_how_to(self):
        self.trigger(self.how_to)

    def trigger_start_menu(self):
        self.trigger(self.back_to_start_menu())

    def turn_everything_off(self):
        self.howToOn = False
        self.deliveryGameOn = False
        self.gameOn = False
        if hasattr(self.scene, 'field'):
            self.scene.purge_silently(self.scene.field)
        try:
            deliveryItems = self.scene.get_list(DeliveryItem)
            for deliveryItem in deliveryItems[::-1]:
                self.scene.purge_silently(deliveryItem)
            # self.toTranslate
        except Exception as e:
            print(e)
        if hasattr(self.scene, 'tronTrain'):
            self.scene.purge_silently(self.scene.tronTrain)
        self.lastTrainHit = 0
        self.currentlyHitting = None

    def trigger(self, action, delay=0, actor=None):  # maybe I need arguments as another argument
        self.actionQueue[self.scene.time+delay] = (action, actor)

    def destroy_menus(self):
        menuItems = self.scene.get_list(MenuItem)
        for menu in menuItems[::-1]:
            self.scene.purge_silently(menu)

    def start_game(self):
        self.scene.add(Field(), 'field')

        self.gameName = self.scene.gameName.text
        self.destroy_menus()
        self.gameOn = True
        self.gamePoints = 0
        self.combo = 0
        self.newPoints = 0
        self.newPointsTimer = 0
        self.fallSpeed = 20
        self.fallSpeedTrigger = 0
        self.main_view.updateGL()

        # self.scene.time = 0

    def how_to(self):
        self.destroy_menus()
        self.howToOn = True
        self.main_view.updateGL()

        # back to main menu button
        backToMainRect = QRect(-80, -80, 80, 15)
        backToMenu = MenuItem("Back to Main", backToMainRect, game=self)
        # secret field: x: -20, -16 # y: 53, 62
        backToMenu.set_clickable(backToMainRect)
        backToMenu.set_action(lambda menu: menu.game.back_to_start_menu())
        self.scene.add(backToMenu, 'gameName')

    def load_dictionary(self):
        # theDict = self.languageDict['swe']
        with open('swedishTranslations.json', 'r', encoding='utf-8') as f:
            s = f.read()
            # jsEncoding = json.detect_encoding(f)

            self.languageDict['swe'] = json.loads(s)

    def start_delivery_tron(self):
        # for now I will close tetris here, later put the closing (and the GAME OVER flash) in a different function
        self.gameOn = False
        # del self.scene.field
        if hasattr(self.scene, 'field'):
            self.scene.purge_silently(self.scene.field)
        self.destroy_menus()

        self.languageDict['swe'] = {}
        self.load_dictionary()

        wordKeys = random.sample(self.languageDict['swe'].keys(), 3)
        print(list([(word, self.languageDict['swe'][word]) for word in wordKeys]))

        self.deliveryGameOn = True
        # deliveryField =
        tronTrain = TronTrain((0, 0))
        self.scene.add(tronTrain, 'tronTrain')

        toTranslate = self.spawn_delivery_item()
        if toTranslate is not None:
            self.spawn_delivery_item(self.languageDict['swe'][toTranslate])

        toTranslate = self.spawn_delivery_item()
        if toTranslate is not None:
            self.spawn_delivery_item(self.languageDict['swe'][toTranslate])


    def spawn_delivery_item(self, next=None):
        randPos = (random.randint(-50, 50), random.randint(-50, 50))
        colliding = True
        while colliding:
            allPositions = [item.pos for item in self.scene.iter_instances(DeliveryItem)] + [self.scene.tronTrain.pos]
            if any([Collision.point_point(randPos, pos, 20) for pos in allPositions]):
                randPos = (random.randint(-50, 50), random.randint(-50, 50))
                continue
            else:
                break

        if self.deliveryMode == 'swe':
            content = next if next else random.choice(list(self.languageDict['swe'].keys()))
            deliveryItem = DeliveryItem(randPos, content=content)
            self.scene.add(deliveryItem)
            return deliveryItem.content

        else:
            deliveryItem = DeliveryItem(randPos, content=str(self.deliveryTronNum))
            self.deliveryTronNum += 1
            self.scene.add(deliveryItem)

    def check_hit(self, tronTrain):
        # train should not hit itself, also train should catch food
        # train should catch food in the right order
        toPurge = []
        hit = False
        hitAnything = False
        # TODO: make depend on deliveryMode, check if correct word, write first-hit-word into a variable
        for item in self.scene.iter_instances(DeliveryItem):
            if Collision.point_point(tronTrain.pos, item.pos, 5):
                # print(item.content, self.lastTrainHit)
                hitAnything = True
                if self.deliveryMode == 'swe':
                    theDict = self.languageDict['swe']
                    if not self.lastTrainHit:
                        self.lastTrainHit = item.content
                        toPurge.append(item)
                    else:
                        if self.lastTrainHit in theDict and item.content == theDict[self.lastTrainHit]\
                                or item.content in theDict and self.lastTrainHit == theDict[item.content]:
                            toPurge.append(item)
                            hit = True
                            self.lastTrainHit = None
                            tronTrain.regenerate_health(2)
                            self.currentlyHitting = None
                        else:
                            if item is not self.currentlyHitting:
                                self.currentlyHitting = item
                                tronTrain.lose_health(10)

                else:
                    if item.content == str(self.lastTrainHit + 1):
                        toPurge.append(item)
                        hit = True
                        self.lastTrainHit = int(item.content)
                        tronTrain.regenerate_health(2)
                        self.currentlyHitting = None
                    else:
                        if item is not self.currentlyHitting:
                            self.currentlyHitting = item
                            tronTrain.lose_health(10)
        if hitAnything is False:
            self.currentlyHitting = None

        for item in reversed(toPurge):
            self.scene.purge_silently(item)

        if self.deliveryMode != 'swe':
            if hit and len(self.scene.get_list(DeliveryItem)) < random.randint(3, 6):
                for n in range(random.randint(2,5)):
                    self.spawn_delivery_item()
        else:
            if hit:
                # spawn two items, just like in the initiation-method of delivery tron
                toTranslate = self.spawn_delivery_item()
                if toTranslate is not None:
                    self.spawn_delivery_item(self.languageDict['swe'][toTranslate])

        # hit itself
        line1 = tronTrain.posHistory[-2:]
        restLines = tronTrain.posHistory[-40:-4]

        if len(restLines) >= 2:
            for i in range(len(restLines)-1):
                segment = (restLines[i], restLines[i+1])
                if Collision.line_line(line1[0][0], line1[0][1], line1[1][0], line1[1][1],
                                       segment[0][0], segment[0][1], segment[1][0], segment[1][1]
                                       ):
                    if segment not in self.selfHitSegments:
                        tronTrain.lose_health(5)
                    self.selfHitSegments.append(segment)

    def back_to_start_menu(self):
        self.init_menus()

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_step)
        self.timer.setInterval(30)
        self.timer.start()

    def toggle_pause(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def time_step(self):
        self.scene.time += 1
        self.inactivityTimer += 1
        if self.gameCheatText.endswith('delivery') and not self.deliveryGameOn:
            self.gameCheatText = ''
            self.start_delivery_tron()

        for timeKey in sorted(self.actionQueue.keys()):
            if self.scene.time > timeKey:
                action, actor = self.actionQueue[timeKey]
                if actor is None:
                    action()
                else:
                    actor.action()
                del self.actionQueue[timeKey]
            else:
                break

        self.timed_happenings()

    def timed_happenings(self):
        val = self.director.animation_step()
        # if val:
        if self.gameOn:
            if self.newPoints:
                self.newPointsTimer += 0.25
                if self.newPointsTimer >= 10:
                    self.newPoints = 0
            if self.scene.time % self.fallSpeed == 0:
                # check_fall()
                # if self.scene.field.currentTetri.alive:
                self.scene.field.currentTetri.fall(True)
        if self.deliveryGameOn:

            self.check_hit(self.scene.tronTrain)
            if self.scene.time % 2 == 0:
                self.scene.tronTrain.move()
        self.main_view.updateGL()

    def check_collision(self):
        # check collisions when spawning, when falling and moving with other blocks and with floor
        pass
