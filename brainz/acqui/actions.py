#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
import logging
from acqui.tasks import Action


class BackgroundAction(Action):

    def __init__(self, color, screen):
        self.color = color
        self.screen = screen
        self.logger = logging.getLogger('logger')

    def onUpdate(self):
        self.screen.fill(self.color)


class CrossAction(Action):

    def __init__(self, imgpath, screen):
        self.img = pygame.image.load(imgpath).convert_alpha()
        self.screen = screen
        self.rect = self.img.get_rect()
        self.rect.center = screen.get_rect().center

    def onUpdate(self):
        self.screen.blit(self.img, self.rect)


class SoundAction(Action):

    def __init__(self, sndfile):

        self.logger = logging.getLogger('logger')
        self.snd = pygame.mixer.Sound(sndfile)

    def onStart(self):

        # self.snd.play()

        pass

    def onStop(self):
        self.logger.debug('play start!')
        self.snd.play()
        self.logger.debug('play stop!')
        pass


class MessageAction(Action):

    def __init__(self, text, screen):
        self.logger = logging.getLogger('logger')
        self.text = text
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.surface = self.font.render(text, True, (10, 10, 10))
        self.rect = self.surface.get_rect()

        # self.rect.move_ip(math.ceil(self.screen.get_size()[0]/2-self.rect.width/2), math.ceil(self.screen.get_size()[1]/2-self.rect.height/2))

        self.rect.center = screen.get_rect().center

    def onUpdate(self):
        self.screen.blit(self.surface, self.rect)


class DataWriteStartAction(Action):

    """docstring for DataDumpAction"""

    def __init__(self, writer):
        self.writer = writer

    def onStart(self):
        self.writer.startWriting()


class DataWriteStopAction(Action):

    """docstring for DataDumpAction"""

    def __init__(self, writer, classPool):
        self.writer = writer
        self.classPool = classPool

    def onStop(self):
        self.writer.stopWriting(self.classPool.current().clazz.orientation)


