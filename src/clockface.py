# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
Provide logic and part of the GUI to manipulate the clockface of the project.

Mostly this module is about arranging the words in a uniform way on the 
clockface and make sure sentences will be displayed with words in the correct
order and no words concatenated.
'''

import gtk
import svg
import rsvg
import math

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Tile(object):
    
    '''
    Define a tile of the clockface. Instances of this class will be assigned
    as attributes to the instances of Element() in the SuperSequence().
    '''

    default_settings = {'matrix_x':0,
                        'matrix_y':0,
                        'draw_box':True,
                        'draw_text':True,
                        'draw_code':False,
                        'tile_color':(255,255,255),
                        'text_color':(255,255,255),
                        'code_color':(255,0,0),
                        'font':'courier',
                        'text_size':40,
                        'code_size':5,
                        'border_size':1}
        
    def __init__(self, selem, **kwargs):
        '''
        selem: instance of supseq.Element()
        '''
        self.selem = selem
        for k,v in self.default_settings.items():
            value = kwargs[k] if k in kwargs else v
            setattr(self, k, value)
        self.x = self.matrix_x * self.text_size
        self.y = self.matrix_y * self.text_size
        self.svg_generation()
        self.cached_xml = ''
        self.protohash = None
        
    def svg_generation(self):
        '''
        Generate the graphical elements that are part of the tile.
        '''
        self.items = []
        self.height = self.text_size
        self.width = self.text_size * len(self.selem.word)
        #rectangle
        self.items.append(svg.Rectangle((self.x, self.y), self.height, 
                                        self.width, self.tile_color))
        #text
        for i, letter in enumerate(self.selem.word):
            x_letter = self.x + i*self.text_size + self.text_size/4
            y_letter = self.y + self.text_size - self.text_size/4
            self.items.append(svg.Text((x_letter, y_letter), letter, 
                                       self.text_size, self.font))
            
    def strarray(self):
        '''
        Generate XML for SVG file (or return cached one).
        '''
        if not self.cached_xml:
            tile_xml = []
            for item in self.items:
                tile_xml.append(' '.join(item.strarray()))
            self.cached_xml = '\n'.join(tile_xml)
        return self.cached_xml
    
    
class ClockFace(object):
    
    '''
    SVG graphic representation of the clockface and methods to alter it.
    '''
    
    def __init__(self, sequence, image_widget, spinbutton):
        '''
        Cols and Rows are the number of characters for the clockface.
        - sequence: instance of class SuperSequence
        - image_widget: image widget for the SVG drawing
        - cols, rows: columns and raws of the matrix (in # of chars)
        '''
        self.sequence = sequence
        self.image_widget = image_widget
        self.spinbutton = spinbutton
        self.max_screen_size = (800, 800)  #Max image size on screen in pixels
        self.adjust_display_params()
        self.spinbutton.set_value(self.cols)
        self.scene = svg.Scene('clockface', width=self.max_screen_size[0], 
                                            height=self.max_screen_size[1])
        # Selection variables
        self.select_color = (255, 255, 0)
        self.unselect_color = (255, 255, 255)
        self.selected_element = 0
        
    def _get_selection_matrix_coords(self):
        '''
        Return a tuple indicating the matrix coordinates of the selected tile.
        '''
        tile = self.sequence[self.selected_element].tile
        return (tile.matrix_x, tile.matrix_y)
        
    def _check_movement_limits(self, direction):
        '''
        Return True if the selection can be moved in the direction without
        falling off the clockface. 
        '''
        # Left and right limits
        if direction == 'left' and self.selected_element == 0 or \
           direction == 'right' and self.selected_element == \
           len(self.sequence)-1:
            return False
        # Upper and lower limits
        y = self._get_selection_matrix_coords()[1]
        if direction == 'up' and y == 0 or \
           direction == 'down' and y == self.get_matrix_footprint()[1]:
            return False
        return True
    
    def adjust_display_params(self, cols=None):
        '''
        Adjust all those properties used to properly size the clockface
        and all graphical elements to properly fit the window.
        '''
        length = self.sequence.get_char_length()
        if cols == None:
            cols = int(math.ceil(math.sqrt(length)))
        self.cols = cols
        self.rows = length/cols + 1
        self.text_size = min(self.max_screen_size[0]/(self.cols+2), 
                             self.max_screen_size[1]/(self.rows+3))
        
    def get_vertical_neighbours(self, best_only=True):
        '''
        Return a tuple the index of the tiles directly over and under 
        the selected one.
        '''
        x, y = self._get_selection_matrix_coords()
        selected_element = self.sequence[self.selected_element]
        occupied_cols = set(range(x, x+len(selected_element.word)))
        upper = []
        lower = []
        for i, elem in enumerate(self.sequence):
            tile = elem.tile
            if tile.matrix_y not in (y-1, y+1):
                continue
            overlapping = set(range(tile.matrix_x, 
                                    tile.matrix_x+len(elem.word))).\
                                    intersection(occupied_cols)
            # Non-overlapping words need to be left too, in case a word at the
            # end of one line has the empty ending of the previous/following
            # line above or under itself.
            entry = (len(overlapping), i)
            if tile.matrix_y == y-1:
                upper.append(entry)
            else:
                lower.append(entry)
        if best_only:
            upper = (0, 0) if not upper else max(upper)
            lower = (0, 0) if not lower else max(lower)
        return (upper, lower)
                         
    def get_matrix_footprint(self):
        '''
        Return a tuple with the max number of cols and lines taken by the 
        matrix.
        '''
        cols = max([elem.tile.matrix_x+elem.get_word_length(strip=True) for 
                    elem in self.sequence])
        rows = self.sequence[-1].tile.matrix_y + 1
        return (cols, rows) 
    
    def get_stats(self):
        '''
        Return clockface statistics.
        '''
        stats = {}
        x, y = self.get_matrix_footprint()
        stats['width'], stats['height'] = str(x), str(y)
        stats['ratio'] = "%.2f" % (x*1.0/y)
        length = self.sequence.get_char_length()
        area = x*y
        wasted = area - length 
        percentage = int(length*100.0/area)
        stats['wasted'] = "%d" % wasted
        stats['optimisation'] = "%d%%" % percentage
        return stats
        
    def arrange_sequence(self):
        '''
        Distribute tiles on the clockface without exceeding the clockface size.
        '''
        cursor = [0, 0]  #insertion point of the tile in the matrix
        for i, element in enumerate(self.sequence):
            if cursor[0] + element.get_word_length(strip=True) > self.cols:
                cursor[0] = 0
                cursor[1] += 1
            is_selected = True if i == self.selected_element else False
            color = self.select_color if is_selected else self.unselect_color
            # Protohashes are tuples unique for a given position/status
            protohash = (cursor[:], element.word, color)
            try:
                cached_protohash = element.protohash
            except AttributeError:
                cached_protohash = None
            # Modify only tiles that have changed since last arrangement but
            # also check the one left to he selected one (it might need an 
            # extra space...
            if protohash != cached_protohash or \
                          element.get_position() == self.selected_element - 1: 
                # Autospacing procedure
                element.word = element.word.strip()
                if element.test_contact():
                    element.word += ' '
                new_tile = Tile(element, 
                                matrix_x=cursor[0], matrix_y=cursor[1], 
                                text_size=self.text_size, tile_color=color)
                new_tile.protohash = protohash
                element.tile = new_tile
            cursor[0] += element.get_word_length()
            
    def change_selection(self, direction):
        '''
        Change the selected tile of the clockface
        '''
        if not self._check_movement_limits(direction):
            return False
        updown = self.get_vertical_neighbours(best_only=True)
        if direction == 'left':
            self.selected_element -= 1
        elif direction == 'right':
            self.selected_element += 1
        elif direction == 'up':
            self.selected_element = updown[0][1]
        elif direction == 'down':
            self.selected_element = updown[1][1]
        
    def move_selected_word(self, direction):
        '''
        Shift the selected tile to either left or right.
        '''
        if not self._check_movement_limits(direction):
            return False
        if self.sequence.shift_element(self.selected_element, direction):
            self.selected_element += +1 if direction == 'right' else -1
            
    def bin_pack(self):
        '''
        Heuristics for footprint optimisation of the clockface. The name
        derives from the Bin Packing Problem. According to wikipedia this 
        implementation should provide at least an OPT + 1 good solution. In
        other words, the clockface could at worst have a line more than the 
        optimal (minimal) solution.
        See http://en.wikipedia.org/wiki/Bin_packing_problem.
        '''
        callback = lambda : self.display(force_update=True)
        # Start from the possible longest word
        self.sequence.move_remaining_longest_next_to(None)
        cursor = 0
        # Keep on adding the longest possible word until line complete or stuck
        while True:
#            self.arrange_sequence()  #recalculate matrix positions
            self.display(force_update=True)
            el = self.sequence[cursor]
            column = el.tile.matrix_x+el.get_word_length()
            self.sequence.move_remaining_longest_next_to(cursor, 
                                                    upper=self.cols-column)
            cursor += 1
            if cursor == len(self.sequence) - 1:
                break
        # If stuck, backtrace
        # If complete, move to the next line
        self.display(force_update=True)
        
    def draw_margins(self):
        min_x, max_x = 0, self.cols*self.text_size
        min_y, max_y = 0, self.rows*self.text_size
        # Vertical
        self.scene.add(svg.Line((max_x, min_y), (max_x, max_y+self.text_size)))
        # Horizontal
        self.scene.add(svg.Line((min_x, max_y), (max_x+self.text_size, max_y)))

    def display(self, force_update=False):
        '''
        Display the clockface.
        - force_update: force gtk to refresh the screen immediately (without
          leaving the gtk main loop to finish it's signal handling).
        '''
        self.arrange_sequence()
        self.scene.items = []
        self.draw_margins()
        for elem in self.sequence:
            self.scene.add(elem.tile)
        xml = self.scene.get_xml()
        rsvg_handler = rsvg.Handle(data=xml.getvalue())
        pixbuf = rsvg_handler.get_pixbuf()
        self.image_widget.set_from_pixbuf(pixbuf)
        if force_update:
            while gtk.events_pending():
                gtk.main_iteration(False)
        

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()