#!/usr/bin/env python
# -*- coding: utf-8  -*-
'''
Virtual wordclock.

Generate, and change on-the-fly the a virtual clock based on a given clockface.
Generate screenshots and all the files to create the project.
'''

import cairo
import gtk
import os

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

    def __new__(cls, chars, size=None, drawing_area=None):
        # Need to use __new__ instead of __init__ as unicode is an immutable
        # type, so overriding __init__it would throw errors.
        # CFR: http://stackoverflow.com/questions/1184337
        cls.cols, cls.rows = size
        cls.drawing_area = drawing_area
        chars = cls.__replace_spaces(cls, chars)
        # To be overridden later on
        cls.font_face = "Courier New"
        cls.min_pixel_dimension = 400
        cls.max_pixel_dimension = 400
        cls.charspace = 1.0
        cls.borderspace = 1.0
        cls.case = None
        cls.italic = False
        cls.bold = False
        cls.bkg_color = gtk.gdk.Color("#000")
        cls.unlit_color = gtk.gdk.Color("#888")
        cls.lit_color = gtk.gdk.Color("#FFF")
        cls.custom_color = gtk.gdk.Color("#800")
        cls.drawing_area.set_size_request(cls.min_pixel_dimension,
                                          cls.min_pixel_dimension)
        return super(VirtualClock, cls).__new__(cls, chars)

    @staticmethod
    def __get_rare_chars(cls, chars):
        '''
        Helper function that return a list of unique chars in "chars" sorted
        from the most rare to the most common one. Return a list of chars.
        '''
        chars = list(chars)
        rare = list(set(chars))
        rare.sort(key=lambda x:chars.count(x))
        rare = [ch for ch in rare if ch != ' ']
        return rare

    @staticmethod
    def __get_neighbours(cls, chars, pos):
        '''
        Helper function that return the 8 chars surrounding the one in
        position "pos" of the chars string. Return a string.
        '''
        get_coord = lambda i : (i%cls.cols, i/cls.cols)
        get_index = lambda x,y : x + y*cls.cols
        is_valid = lambda x,y : True if 0 <= x < cls.cols and \
                                        0 <= y < cls.rows else False
        chars = list(chars)
        x, y = get_coord(pos)
        neighbours_pos = [get_index(xx, yy) for xx in range(x-1, x+2) for
                                                yy in range(y-1, y+2) if
                                                is_valid(xx, yy)]
        neighbours_pos.remove(pos)
        return ''.join([chars[i] for i in neighbours_pos])

    @staticmethod
    def __replace_spaces(cls, chars):
        '''
        Replace spaces on the clockface with random chars taken from the pool
        of existing chars. Pick the most rare ones, making sure it is not
        one of the 8 bordering ones.
        '''
        chars = list(chars)
        for pos, char in enumerate(chars):
            rare = cls.__get_rare_chars(cls, chars)  #rarity changes with repl.
            if char == ' ':
                neighbours = cls.__get_neighbours(cls, chars, pos)
                for r in rare:
                    if r not in neighbours + "'\"!-":
                        chars[pos] = r
                        break
        return ''.join(chars)

    def __font_face_stripping(self):
        '''
        Strip font face information by noise that prevent cairo to display it.
        Cairo "select_font_face" is just a "toy", so we need to strip
        the font description of size and modifiers to attempt making it
        more accurate. No guarantees it works though!
        CFR: http://www.cairographics.org/manual/cairo-text.html
        '''
        noisy_words = ['Italic', 'Bold', 'Regular', 'Plain', 'Normal',
                       'Oblique', 'Normal', 'Light', 'Medium', 'Condensed',
                       'Roman', 'Demi', 'Thin', 'Heavy']
        tmp = self.font_face.split()
        tmp = [e for e in tmp if e not in noisy_words and not e.isdigit()]
        self.font_face = ' '.join(tmp)

    def refresh_params(self, **kwargs):
        '''
        Recalculate all the parameters needed for drawing the clockface.
        Can accept keyword arguments to change values.
        '''
        for k in kwargs:
            setattr(self, k, kwargs[k])
        self.__font_face_stripping()
        self.scaling = float(self.max_pixel_dimension)/max(self.cols,
                                                           self.rows)
        self.size_x, self.size_y = int(self.cols*self.scaling), \
                                   int(self.rows*self.scaling)

    def update(self):
        self.refresh_params()
        self.drawing_area.window.clear()
        surface = self.drawing_area.window.cairo_create()
        self.draw(surface)

    def draw(self, surface):
        '''
        Draw the clock on the surface.
        '''
        gtk_to_rgb = lambda x : [c/65535.0 for c in (x.red, x.green, x.blue)]
        cr = surface
        # NORMALISATION
        cr.scale(self.size_x, self.size_y)
        # EM [one char size, in percentage of normalised surface]
        ems_in_matrix_unit = 1.0+self.charspace
        ems_in_border = self.borderspace
        em_x = 1/(ems_in_border*2+ems_in_matrix_unit*(self.cols-1)+1)
        em_y = 1/(ems_in_border*2+ems_in_matrix_unit*(self.rows-1)+1)
        # BACKGROUND
        cr.save()
        cr.set_source_rgb(*gtk_to_rgb(self.bkg_color))
        cr.rectangle(0, 0, 1, 1)
        cr.fill()
        cr.restore()
        # FONT SETTINGS
        slant = cairo.FONT_SLANT_ITALIC if \
                            self.italic else cairo.FONT_SLANT_NORMAL
        weight = cairo.FONT_WEIGHT_BOLD if \
                            self.bold else cairo.FONT_WEIGHT_NORMAL
        cr.select_font_face(self.font_face, slant, weight)
        cr.set_source_rgb(*gtk_to_rgb(self.unlit_color))
        # LETTER OUTPUT
        cr.scale(em_x, em_y)  #normalisation to em = 1.0
        cr.set_font_size(1.0)
        fascent, fdescent, fheight, fxadvance, fyadvance = cr.font_extents()
        cx, cy = 0, 0
        cr.translate(ems_in_border, ems_in_border)
        for letter in self:
            if self.case == 'lower':
                letter = letter.lower()
            elif self.case == 'upper':
                letter = letter.upper()
            xbearing, ybearing, width, height, xadvance, yadvance = \
                                                    cr.text_extents(letter)
            cr.move_to(cx*ems_in_matrix_unit + 0.5 - xbearing - width / 2,
                       cy*ems_in_matrix_unit + 0.5 - fdescent + fheight / 2)
            cr.show_text(letter)
            if cx == self.cols-1:
                cy += 1
                cx = 0
            else:
                cx += 1
#        cr.show_page()

    def get_shot(self, format):
        '''
        Return a file in either 'svg' or 'png' formats.
        '''
        fname = 'cface_shot' + '.' + format
        self.refresh_params()
        if format == 'svg':
            surface = cairo.SVGSurface(fname, self.size_x, self.size_y)
        else:
            raise BaseException("Allowed file formats: 'svg', 'png'.")
        self.draw(cairo.Context(surface))
        surface.finish()
        to_perc = lambda x : str(int(round(x*100)))
        new_name = '_'.join((self.font_face,
                             to_perc(self.charspace),
                             to_perc(self.borderspace)))
        if self.italic:
            new_name += '_italic'
        if self.bold:
            new_name += '_bold'
        if self.case:
            new_name += '_' + self.case
        new_name += '.' + format
        os.rename(fname, new_name)

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!\n')
    cols, rows = 5, 3
    chars = '01 34 b d AB DE'
    print('Input string → %s' % chars)
    for r in [chars[i*cols:i*cols+cols] for i in range(rows)]:
        print(r)
    vc = VirtualClock(chars, size=(cols,rows), image_widget=None)
    print('\nVC → %s' % vc)
    for r in [vc[i*cols:i*cols+cols] for i in range(rows)]:
        print(r)

if __name__ == '__main__':
    run_as_script()