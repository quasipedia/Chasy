#!/usr/bin/env python
# -*- coding: utf-8  -*-
'''
Virtual wordclock.

Generate, and change on-the-fly the a virtual clock based on a given clockface.
Generate screenshots and all the files to create the project.
'''

import  cairo

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class VirtualClock(object):

    '''
    The virttual clock
    '''

    def __init__(self, chars, size, image_widget):
        self.max_pixel_dimension = 800
        self.chars = chars
        self.cols, self.rows = size
        self.image = image_widget
        self.go()

    def go(self):
        # Define dimensions
        self.max_pixel_dimension = 800
        scaling = float(self.max_pixel_dimension)/max(self.cols, self.rows)
        size_x, size_y = int(self.cols*scaling), int(self.rows*scaling)
        self.surface = cairo.SVGSurface('clockface.svg', size_x, size_y)
        cr = self.cr = cairo.Context(self.surface)
        cr.scale(size_x, size_y)  #Normalise as it scales to full size
        # Start writing!
        cr.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cr.scale(1.0/self.cols, 1.0/self.rows)
        cr.set_font_size(1.0)
        fascent, fdescent, fheight, fxadvance, fyadvance = cr.font_extents()
        cx, cy = 0, 0
        for letter in self.chars:
            xbearing, ybearing, width, height, xadvance, yadvance = \
                                                    cr.text_extents(letter)
            cr.move_to(cx + 0.5 - xbearing - width / 2,
                       cy + 0.5 - fdescent + fheight / 2)
            cr.show_text(letter)
            if cx == self.cols-1:
                cy += 1
                cx = 0
            else:
                cx += 1
#        cr.show_page()
        self.surface.finish()

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()