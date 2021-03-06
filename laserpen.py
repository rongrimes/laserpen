#!/usr/bin/env python3

from laserimage import *
import pantilthat
import RPi.GPIO as GPIO
import time

#---------------------------------------------------------------
class LaserPen:
    # Constants for the Pimoroni Pan-Tilt platform.
    servo_p = 1
    servo_t = 2

    pan_max = 2500
    pan_min = 550
    tilt_max = 2600
    tilt_min = 875

    laser_pin = 18
    PWR_OFF = 0
    PWR_MAX = 100

    def __init__(self):
        self.incr_offset_x = False 
        self.incr_offset_y = False   # True for pen led side, False for pen ethernet side.

        self.curr_x = 0
        self.curr_y = 0
        self.pwr = 0
        self.run = True    # Always True, except when set to False to cancel a
                           #        drawing operation.

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.laser_pin, GPIO.OUT)  # activate output
        self.laser_pwm = GPIO.PWM(self.laser_pin, 100)  # duty cycle: 100Hz
        self.laser_pwm.start(0)

        self._init_pantilt()

    def _init_pantilt(self):
        pantilthat.idle_timeout(0.5)
        pantilthat.servo_pulse_min(LaserPen.servo_p, LaserPen.pan_min)
        pantilthat.servo_pulse_max(LaserPen.servo_p, LaserPen.pan_max)
        pantilthat.servo_pulse_min(LaserPen.servo_t, LaserPen.tilt_min)
        pantilthat.servo_pulse_max(LaserPen.servo_t, LaserPen.tilt_max)

    def _pan(self, value):
        if value == self.curr_x:   # already there, don't waste time
            return
#       print("pan: ", value)

        try:
            pantilthat.pan(value)
        except Exception as e:  # example: value outside [-90,90] is presented.
            print(str(e))

        self.curr_x = value 
        time.sleep(DataDict["short_wait"])

    def _tilt(self, value):
        if value == self.curr_y:   # already there, don't waste time
            return
#       print("tilt:", value)

        try:
            pantilthat.tilt(value)
        except Exception as e:  # example: value outside [-90,90] is presented.
            print(str(e))

        self.curr_y = value 
        time.sleep(DataDict["short_wait"])

    def laser_pwr(self, value):
        self.laser_pwm.ChangeDutyCycle(value)

    def _map(self, incr_offset, laser_coord, lbound):
        if incr_offset:
            return laser_coord + lbound
        else:
            return lbound - laser_coord

    def _move(self, x, y):  # x,y use image co-ordinate set

        print(f"move > ({str(x)}, {str(y)})")
        if x > self.image_width or y > self.image_height:
#           raise ValueError("x,y parms to 'laserpen.move' outside image size.")
            print("laserpen.move: ({}, {}) outside image bounds, ignored.".format(x,y))

#       pos_x, pos_y are in the laserpen co-ordinate system
        pos_x = self._map(self.incr_offset_x, int(x/self.image_width  * self.axis_lx), self.lb_x)
        pos_y = self._map(self.incr_offset_y, int(y/self.image_height * self.axis_ly), self.lb_y)

#       print(x, y, pos_x, pos_y, self.axis_lx, self.axis_ly, self.lb_x, self.lb_y)
        xy_steps = [(pos_x, pos_y)]
        self.laser_pwr(self.PWR_OFF)
        self._pan(pos_x)
        self._tilt(pos_y)

    def _line(self, pwr, x, y, fast_move=False):  # x,y use image co-ordinate set
        print(f"move > ({str(x)}, {str(y)})")
        if x > self.image_width or y > self.image_height:
            print(f"laserpen.move: ({x}, {y}) outside image bounds, ignored.")

#       pos_x, pos_y are in the laserpen co-ordinate system
        pos_x = self._map(self.incr_offset_x, int(x/self.image_width  * self.axis_lx), self.lb_x)
        pos_y = self._map(self.incr_offset_y, int(y/self.image_height * self.axis_ly), self.lb_y)

#       print(x, y, pos_x, pos_y, self.axis_lx, self.axis_ly, self.lb_x, self.lb_y)
        if fast_move:
            xy_steps = [(pos_x, pos_y)]
        else:
            x_delta = pos_x - self.curr_x
            y_delta = pos_y - self.curr_y

            longer  = max(abs(x_delta), abs(y_delta))
            no_of_steps = int(longer // DataDict["pantilt_step"])
#           print(pos_x, pos_y, self.curr_x, self.curr_y, x_delta, y_delta, longer)

            xy_steps = []

            for r in range(1, no_of_steps+1):
                xx = int(r * x_delta / no_of_steps) + self.curr_x
                yy = int(r * y_delta / no_of_steps) + self.curr_y
                xy_steps.append((xx,yy))

        self._draw_steps(xy_steps, pwr)

    def _draw_steps(self, xy_steps, pwr):
    #   print(xy_steps)
    #   See if we can move with laser on, or invisibly
    #   Criteria: if all x coords are equal, or all y co-ords are equal.
        move_visibly = all(co_ord == xy_steps[0][0] for (co_ord, _) in xy_steps) or \
                       all(co_ord == xy_steps[0][1] for (_, co_ord) in xy_steps)

        self.laser_pwr(self.PWR_OFF)
        for x,y in xy_steps:
            if self.run:     # set to False in lasergui if Cancel button pressed
                if move_visibly:
                    self.laser_pwr(pwr)
                else:
                    self.laser_pwr(self.PWR_OFF)
                self._pan(x)
                self._tilt(y)

                if move_visibly == False:
                    self.laser_pwr(pwr)
                    time.sleep(DataDict["short_wait"])
                    self.laser_pwr(self.PWR_OFF)
            else:
                break
        self.laser_pwr(self.PWR_OFF)

    def render_image(self, image):
        print("render image")
        self.image_width  = image.dimensions[0]
        self.image_height = image.dimensions[1]

        self.run = True
        for pwr, x, y, speed in image.steps:
            if self.run:     # set to False in lasergui if Cancel button pressed
                self._line(pwr, x, y, fast_move=speed)
            else:
                break

    def _bounds_error(self, origin_val, range_val, axis, incr_offset):
        lb = origin_val if incr_offset else origin_val - range_val
        ub = origin_val + range_val if incr_offset else origin_val
#       print(lb, ub)
        if lb >  90 or ub > 90:
            raise ValueError(axis + " bound out of range: Must be < 90.")
        elif lb < -90 or ub < -90:
            raise ValueError(axis + " bound out of range: Must be > -90.")
        return False

    def set_bounds(self, origin, pt_range):
        # mapping: True: laser point = image point + lb
        #         False: laser point = lb - image point
        if self._bounds_error(origin[0], pt_range[0], 'x', self.incr_offset_x) or \
           self._bounds_error(origin[1], pt_range[1], 'y', self.incr_offset_y):
            return

        self.lb_x = origin[0]
        self.axis_lx = pt_range[0]
        self.lb_y = origin[1]
        self.axis_ly = pt_range[1]
        self._set_init_pos(origin)

    def _set_init_pos(self, origin):
#       print("Start postion: (0,0)")
        self._pan (origin[0])
        self._tilt(origin[1])

#--------------------------------------------------------------

if __name__ == "__main__":
    image = Image()

    laserpen = LaserPen()
    try:
        laserpen.set_bounds(DataDict["pantilt_origin"], DataDict["pantilt_range"])
    except ValueError as e:
        print(str(e))
        quit()    

    laserpen.set_init_pos((0,0))

    try:
        for i in range(5):
            image.box_100(laserpen, fast=True)

        print()
        for i in range(1):
            image.box_100(laserpen, fast=False)

    except KeyboardInterrupt:
        print("\n")
