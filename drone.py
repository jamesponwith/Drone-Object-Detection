from djitellopy import Tello
import cv2
import pygame
import pygame.locals
# from pygame.locals import *
import numpy as np
import time
from controller import PS4Controller
from yolo_video import Yolo

# Speed of the drone
S = 60
# Frames per second of the pygame window display
FPS = 25
TIME_TO_WAIT = 0.5 # in seconds


class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations
            - W and S: Up and down.
    """

    def __init__(self):
        # Init pygame
        self.ps4 = PS4Controller()
        self.ps4.init()

        self.yolo = Yolo()

        self.yolo_on = True

        # pygame.init()

        # Creat pygame window
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False

        # create update timer
        pygame.time.set_timer(pygame.locals.USEREVENT + 1, 50)

    def handle_cmd(self, cmd):
        if len(cmd) == 2:
            if cmd[0] == 'flip':
                self.tello.flip(cmd[1])
            else:
                self.move(cmd[0], cmd[1])
        elif cmd == 'update':
            self.update()
        elif cmd == 'takeoff':
            self.send_rc_control = True
            self.tello.takeoff()
        elif cmd == 'land':
            self.send_rc_control = False
            self.tello.land()
        elif cmd == 'emergency':
            self.send_rc_control = False
            self.tello.emergency()
            return True
        elif cmd == 'n_n':
            self.yolo_on = not self.yolo_on
        return False
            # should_stop = True
            # break


    def run(self):
        if not self.tello.connect():
            print("Tello not connected")
            return

        if not self.tello.set_speed(self.speed):
            print("Not set speed to lowest possible")
            return

        # In case streaming is on.
        # This happens when we quit this program without the escape key.
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return

        frame_read = self.tello.get_frame_read()

        should_stop = False
        while not should_stop:
            time.sleep(0.01)
            for cmd in self.ps4.get_controls(): # maybe not make this a generator
                should_stop = self.handle_cmd(cmd)
                if should_stop:
                    break
            # for event in pygame.event.get():
                # # print(event)
                # if event.type == pygame.locals.USEREVENT + 1:
                    # self.update()
                # elif event.type == pygame.locals.QUIT:
                    # should_stop = True
                # elif event.type == pygame.locals.KEYDOWN:
                    # if event.key == pygame.locals.K_ESCAPE:
                        # should_stop = True
                    # else:
                        # self.keydown(event.key)
                # elif event.type == pygame.locals.KEYUP:
                    # self.keyup(event.key)

            if frame_read.stopped:
                frame_read.stop()
                break


            self.screen.fill([0, 0, 0])
            frame = frame_read.frame
            if self.yolo_on:
                frame = self.yolo.do_yolo(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)

        # Call it always before finishing. I deallocate resources.
        self.tello.end()


    def move(self, direction, value):
        if direction == 'forward':
            self.for_back_velocity = S
        elif direction == 'back':
            self.for_back_velocity = -S
        elif direction == 'left':
            self.left_right_velocity = -S
        elif direction == 'right':
            self.left_right_velocity = S
        elif direction == 'up':
            if value:
                self.up_down_velocity = S
            else:
                self.up_down_velocity = 0
        elif direction == 'down':
            if value:
                self.up_down_velocity = -S
            else:
                self.up_down_velocity = 0
        elif direction == 'cw':  # set yaw clockwise velocity
            if value:
                self.yaw_velocity = -S
            else:
                self.yaw_velocity = 0 
        elif direction == 'ccw':  # set yaw counter clockwise velocity
            if value:
                self.yaw_velocity = S
            else:
                self.yaw_velocity = 0 
        elif direction == 'reset':
            self.reset_movement()

    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # set yaw clockwise velocity
            self.yaw_velocity = -S
        elif key == pygame.K_d:  # set yaw counter clockwise velocity
            self.yaw_velocity = S


    def reset_movement(self):
        self.for_back_velocity   = 0
        self.for_back_velocity   = 0
        self.left_right_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity    = 0
        self.up_down_velocity    = 0
        self.yaw_velocity        = 0
        self.yaw_velocity        = 0


    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            self.tello.land()
            self.send_rc_control = False


    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            self.tello.send_rc_control(
                    self.left_right_velocity,
                    self.for_back_velocity,
                    self.up_down_velocity,
                    self.yaw_velocity)
            # self.reset_movement()


def main():
    frontend = FrontEnd()
    # run frontend
    frontend.run()


if __name__ == '__main__':
    main()
