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


class VirtualClock(unicode):

    '''
    The virtual clock. Inherits from unicode string. Must be singleton.
    '''

    def __new__(cls, chars, size=None, image_widget=None):
        # Need to use __new__ instead of __init__ as unicode is an immutable
        # type, so overriding __init__it would throw errors.
        # CFR: http://stackoverflow.com/questions/1184337
        cls.max_pixel_dimension = 800
        cls.cols, cls.rows = size
        cls.chars = chars
        cls.__replace_spaces(cls)
        cls.image = image_widget
        return super(VirtualClock, cls).__new__(cls, chars)

    @staticmethod
    def __get_rare_chars(cls):
        '''
        Helper function that return a list of unique chars in "chars" sorted
        from the most rare to the most common one. Return a list of chars.
        '''
        chars = list(cls.chars)
        rare = list(set(chars))
        rare.sort(key=lambda x:chars.count(x))
        rare = [ch for ch in rare if ch != ' ']
        return rare

    @staticmethod
    def __get_neighbours(cls, pos):
        '''
        Helper function that return the 8 chars surrounding the one in
        position "pos" of the chars string. Return a list of chars.
        '''
        get_coord = lambda i : (i%cls.cols, i/cls.cols)
        get_index = lambda x,y : x + y*cls.cols
        is_valid = lambda x,y : True if 0 <= x < cls.cols and \
                                        0 <= y < cls.rows else False
        chars = list(cls.chars)
        x, y = get_coord(pos)
        neighbours_pos = [get_index(xx, yy) for xx in range(x-1, x+2) for
                                                yy in range(y-1, y+2) if
                                                is_valid(xx, yy)]
        neighbours_pos.remove(pos)
        print('ORIG: %s  NEAR: %s' % (str(pos), str(sorted(neighbours_pos))))
        return ''.join([chars[i] for i in neighbours_pos])

    @staticmethod
    def __replace_spaces(cls):
        '''
        Replace spaces on the clockface with random chars taken from the pool
        of existing chars. Pick the most rare ones, making sure it is not
        one of the 8 bordering ones.
        '''
        chars = list(cls.chars)
        rare = cls.__get_rare_chars(cls)
        for pos, char in enumerate(chars):
            if char == ' ':
                neighbours = cls.__get_neighbours(cls, pos)
                for r in rare:
                    if r not in neighbours:
                        chars[pos] = r
                        break

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
    cols, rows = 5, 3
    chars = '01 34 b d AB DE'
#    chars = ''.join([chr(x) for x in range(33, 33+cols*rows)])
    for r in [chars[i*cols:i*cols+cols] for i in range(rows)]:
        print(r)
    vc = VirtualClock(chars, size=(cols,rows), image_widget=None)
    print('VC=', vc)
    vc.go()

if __name__ == '__main__':
    run_as_script()