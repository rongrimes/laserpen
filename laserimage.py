#!/usr/bin/env python3

from datadict import DataDict
from guizero import App
from lasersvg import LoadSvg

#---------------------------------------------------------------
class Image:
    PWR_OFF = 0
    PWR_MAX = 100

    def __init__(self):
        self.width  = 0
        self.height = 0
        

    def bounds(self, x, y):
        self.dimensions  = (x, y)

    def box_100(self, laserpen):
        self.dimensions = (100, 100)
        pwr = self.PWR_MAX
        self.steps = [(self.PWR_OFF, 0,0,True), (pwr, 100,0,False), \
                (pwr, 100,100,True), (pwr, 0,100,False), (pwr, 0,0,True)]
        laserpen.render_image(self)

    def draw_quickbox(self, app, laserpen):
        '''Draws the outer frame of the drawing to facilitate post drawing stretching.
        '''
        self.dimensions = (100, 100)
        pwr = self.PWR_MAX
        self.steps = [(self.PWR_OFF, 0,0,True), (pwr, 100,0,True), \
                (pwr, 100,100,True), (pwr, 0,100,True), (pwr, 0,0,True)]
        laserpen.render_image(self)

    def draw_image(self, app, laserpen):
        global svg_contents
        self.dimensions = svg_contents.dimensions
        self.steps = svg_contents.steps
        laserpen.render_image(self)

    def load_image(self, app):
        global svg_contents
        svg_contents = LoadSvg(self.filename)
        self.validfile = svg_contents.validfile

#--------------------------------------------------------------
if __name__ == "__main__":
    image = Image()

    try:
        pass
    except KeyboardInterrupt:
        print("\n")
