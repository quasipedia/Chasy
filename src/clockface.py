# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
Provide logic and part of the GUI to manipulate the clockface of the project.

Mostly this module is about arranging the words in a uniform way on the 
clockface and make sure sentences will be displayed with words in the correct
order and no words concatenated.
'''

import svg
import rsvg

__author__ = "Mac Ryan"
__copyright__ = "Copyright ${year}, Mac Ryan"
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
    
    def __init__(self, sequence, cols, rows, image_widget):
        '''
        Cols and Rows are the number of characters for the clockface.
        - sequence: instance of class SuperSequence
        - image_widget: image widget for the SVG drawing
        - cols, rows: columns and raws of the matrix (in # of chars)
        '''
        self.sequence = sequence
        self.image_widget = image_widget
        max_screen_size = (800, 800)  #Max image size on screen in pixels
        self.text_size = min(max_screen_size[0]/(cols+3), 
                             max_screen_size[1]/(rows+3))
        self.cols = cols
        self.rows = rows
        self.scene = svg.Scene('clockface', width=max_screen_size[0], 
                                            height=max_screen_size[1])
        # Selection variables
        self.highlight_color = (0, 127, 0)
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
            if not overlapping:
                continue
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
        cols = max([elem.tile.matrix_x+len(elem.word) for 
                    elem in self.sequence])
        rows = self.sequence[-1].tile.matrix_y
        return (cols, rows) 
        
    def arrange_sequence(self):
        '''
        Distribute tiles on the clockface without exceeding the clockface size.
        '''
        cursor = [0, 0]  #insertion point of the tile in the matrix
        for i, element in enumerate(self.sequence):
            wl = len(element.word.decode('utf-8'))
            if cursor[0] + wl > self.cols:
                cursor[0] = 0
                cursor[1] += 1
            is_selected = True if i == self.selected_element else False
            # Protohashes are tuples unique for a given position/status
            protohash = (cursor[:], element.word, is_selected)
            try:
                cached_protohash = element.protohash
            except AttributeError:
                cached_protohash = None
            # Modify only tiles that have changed since last arrangement
            if protohash != cached_protohash:
                color = (255, 255, 0) if is_selected else (255, 255, 255)
                new_tile = Tile(element, 
                                matrix_x=cursor[0], matrix_y=cursor[1], 
                                text_size=self.text_size, tile_color=color)
                new_tile.protohash = protohash
                element.tile = new_tile
            cursor[0] += wl
            
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
        self.arrange_sequence()
        
    def move_selected_word(self, direction):
        '''
        Shift the selected tile to either left or right.
        '''
        if not self._check_movement_limits(direction):
            return False
        if self.sequence.shift_element(self.selected_element, direction):
            self.selected_element += +1 if direction == 'right' else -1
            self.arrange_sequence()
                
    def toggle_grid(self):
        '''
        Toggle visibility of the grid.
        '''
        self.grid_visible = not self.grid_visible
        if self.grid_visible:
            for c in range(self.cols):
                self.scene.add(svg.Line((c*self.text_size, 0), 
                                        (c*self.text_size, self.scene.height)))
            for r in range(self.rows):
                self.scene.add(svg.Line((0, r*self.text_size), 
                                        (self.scene.width, r*self.text_size)))
        
    def draw_margins(self):
        self.scene.add(svg.Line((self.cols*self.text_size, 0),
                                (self.cols*self.text_size, 
                                 self.rows*self.text_size)))
        self.scene.add(svg.Line((0, self.rows*self.text_size),
                                (self.cols*self.text_size, 
                                 self.rows*self.text_size)))
        self.grid_visible=False

    def display(self):
        '''
        Display the clockface.
        '''
        self.scene.items = []
        self.draw_margins()
        for elem in self.sequence:
            self.scene.add(elem.tile)
        xml = self.scene.get_xml()
        rsvg_handler = rsvg.Handle(data=xml.getvalue())
        pixbuf = rsvg_handler.get_pixbuf()
        self.image_widget.set_from_pixbuf(pixbuf)
        

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()