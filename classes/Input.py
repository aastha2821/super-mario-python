import pygame
from pygame.locals import *
import sys


class Input:
    def __init__(self, entity):
        self.entity = entity

    def checkForInput(self):
        events = pygame.event.get()

        # FIRST PRIORITY = QUIZ CLICK
        if hasattr(self.entity.levelObj, "show_quiz") and self.entity.levelObj.show_quiz:
            self.handleQuizClick(events)
            return    # block keyboard/mouse movement while quiz is active

        # NORMAL GAME INPUT (only when quiz is NOT active)
        self.checkForKeyboardInput()
        self.checkForMouseInput(events)
        self.checkForQuitAndRestartInputEvents(events)

    # ------------------------------ QUIZ HANDLING ------------------------------
    def handleQuizClick(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, r in enumerate(self.entity.levelObj.option_rects):
                    if r.collidepoint(mouse_pos):
                        import main

                        if i == self.entity.levelObj.quiz_question["answer"]:
                            # Correct
                            main.current_question += 1
                            self.entity.levelObj.show_quiz = False
                        else:
                            # Wrong → Mario dies (restart)
                            self.entity.restart = True
                        return  # stop checking clicks

    # ------------------------------ NORMAL GAME INPUT ------------------------------
    def checkForKeyboardInput(self):
        pressed = pygame.key.get_pressed()

        if pressed[K_LEFT] or pressed[K_h] and not pressed[K_RIGHT]:
            self.entity.traits["goTrait"].direction = -1
        elif pressed[K_RIGHT] or pressed[K_l] and not pressed[K_LEFT]:
            self.entity.traits["goTrait"].direction = 1
        else:
            self.entity.traits["goTrait"].direction = 0

        jumping = pressed[K_SPACE] or pressed[K_UP] or pressed[K_k]
        self.entity.traits["jumpTrait"].jump(jumping)

        self.entity.traits["goTrait"].boost = pressed[K_LSHIFT]

    def checkForMouseInput(self, events):
        mouseX, mouseY = pygame.mouse.get_pos()

        # RIGHT click — spawn mobs
        if self.isRight(events):
            self.entity.levelObj.addKoopa(mouseY / 32, mouseX / 32 - self.entity.camera.pos.x)
            self.entity.levelObj.addGoomba(mouseY / 32, mouseX / 32 - self.entity.camera.pos.x)
            self.entity.levelObj.addRedMushroom(mouseY / 32, mouseX / 32 - self.entity.camera.pos.x)

        # LEFT click — add coin
        if self.isLeft(events):
            self.entity.levelObj.addCoin(mouseX / 32 - self.entity.camera.pos.x, mouseY / 32)

    def checkForQuitAndRestartInputEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_F5):
                self.entity.pause = True
                self.entity.pauseObj.createBackgroundBlur()

    def isLeft(self, events):
        return self.checkMouse(events, 1)

    def isRight(self, events):
        return self.checkMouse(events, 3)

    def checkMouse(self, events, button):
        for e in events:
            if e.type == pygame.MOUSEBUTTONUP and e.button == button:
                return True
        return False
