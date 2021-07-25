#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
PS4 Controller pygame link

'''

import os
import pprint
import pygame

def ds_to_tello(kind, key, value):
    """if kind == 'axis':
        if key == 0:
            if abs(value) < 0.1:
                return ('reset', 'lr')
            if value < 0:
                return ('left, 20')
            return ('right',  20)
        if key == 1:
            if abs(value) < 0.1:
                return ('reset', 'fb')
            if value < 0:
                return ('forward', 20)
            return 'back 20'
        if key == 3:
            if abs(value) < 0.1:
                return ('reset', 'cw')
            if value < 0:
                return ('ccw', 20)
            return ('cw', 20)
        if key == 4:
            if abs(value) < 0.1:
                return ('reset', 'ud')
            if value < 0:
                return ('up', 20)
            return ('down', 20)"""
    if kind == 'hat':
        print(value)
        # if event.value == (1,0)    
        if value == (1, 0):
            # go right 
            print("right")
            return("right", 20)
        if value == (-1, 0):
            # go left
            print("left")
            return("left", 20)
        if value == (0, 1):
            # go up 
            print("forward")
            return("forward", 20)
        if value == (0, -1):
            # go down
            print("back")
            return("back", 20)
        if value == (0, 0):
            return ('reset', 0)
    if kind == 'button_down':
        if key == 0: # x 
            return 'land'
        if key == 1:
            return ('flip', 'r')
        if key == 3:
            return ('flip', 'l')
        if key == 2: # triangle
            return 'takeoff'
        if key == 4: # L1
            return ('ccw', 20)
        if key == 5: # R1
            return ('cw', 20)
        if key == 6: # r2
            return ('down', 20)
        if key == 7: # r2
            return ('up', 20)
        if key == 8:
            return 'n_n'
        if key == 9:
            return 'streamoff'
        if key == 10:
            return 'emergency'
    if kind == 'button_up':
        if key == 4: # L1
            return ('ccw', 0)
        if key == 5: # R1
            return ('cw', 0)
        if key == 6: # r2
            return ('down', 0)
        if key == 7: # r2
            return ('up', 0)

class PS4Controller(object):
    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

    def event_to_tello(self, event):
        if not event: return None

        if not self.axis_data:
            self.axis_data = {}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        if event.type == pygame.JOYAXISMOTION:
            self.axis_data[event.axis] = round(event.value, 2)
            return ds_to_tello('axis', event.axis, round(event.value, 2)) 
        elif event.type == pygame.JOYBUTTONDOWN:
            self.button_data[event.button] = True
            return ds_to_tello('button_down', event.button, None)
            # kind, data = 'button_down', self.button_data
        elif event.type == pygame.JOYBUTTONUP:
            self.button_data[event.button] = False
            return ds_to_tello('button_up', event.button, None)
            # kind, data = 'button_up', self.button_data
        elif event.type == pygame.JOYHATMOTION:
            self.hat_data[event.hat] = event.value
            return ds_to_tello('hat', event.hat, event.value)
          #  print(event)
            # kind, data = 'hat', self.hat_data
        elif event.type == pygame.locals.USEREVENT + 1:
            return 'update'
        return None


    def get_controls(self):
        return [self.event_to_tello(e) for e in pygame.event.get() if self.event_to_tello(e)]

    def listen(self):
        """Listen for events to happen"""

        if not self.axis_data:
            self.axis_data = {}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        while True:
            ret = []
            for event in pygame.event.get():
                cmd = None
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value, 2)
                    # cmd = ds_to_tello('axis', event.axis, round(event.value, 2)) 
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                    cmd = ds_to_tello('button_down', event.button, None)
                    # kind, data = 'button_down', self.button_data
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                    # kind, data = 'button_up', self.button_data
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value
                    cmd = ds_to_tello('hat', event.hat, event.value)
                    # kind, data = 'hat', self.hat_data
                if cmd:
                    ret.append(cmd)
               # print(event)
            # return ret
                # os.system('clear')
                # pprint.pprint(self.button_data)
                # pprint.pprint(self.axis_data)
                # pprint.pprint(self.hat_data)


if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
