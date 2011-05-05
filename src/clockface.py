# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
Created on 4 May 2011

@author: mac
'''

import svg
import rsvg


class Tile(object):
    
    '''
    Define a tile of the clockface.
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
        
    def __init__(self, word, **kwargs):
        self.word = word.decode('utf-8')
        for k,v in self.default_settings.items():
            value = kwargs[k] if k in kwargs else v
            setattr(self, k, value)
        self.x = self.matrix_x * self.text_size
        self.y = self.matrix_y * self.text_size
        self.tile_generation()
        self.cached_xml = ''
        
    def tile_generation(self):
        '''
        Generate the graphical elements that are part of the tile.
        '''
        self.items = []
        self.height = self.text_size
        self.width = self.text_size * len(self.word)
        #rectangle
        self.items.append(svg.Rectangle((self.x, self.y), self.height, 
                                        self.width, self.tile_color))
        #text
        for i, letter in enumerate(self.word):
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
    SVG graphic representation of the clockface.
    '''
    
    def __init__(self, cols, rows, image_widget):
        '''
        Cols and Rows are the number of characters for the clockface.
        '''
        self.image_widget = image_widget
        max_screen_size = (800, 800)  #Max image size on screen in pixels
        self.text_size = min(max_screen_size[0]/(cols+3), 
                             max_screen_size[1]/(rows+3))
        self.cols = cols
        self.rows = rows
        self.scene = svg.Scene('clockface', width=max_screen_size[0], 
                                            height=max_screen_size[1])
        # Initialise tile collection
        self.tiles = []
        # Selection variables
        self.selected_tile = 0
        self.highlight_color = (0, 127, 0)
        
    def arrange_sequence(self, sequence=None):
        '''
        Distribute tiles on the clockface without exceeding the clockface size.
        '''
        if sequence == None:  #...then one expects cached values to be there!
            assert self.sequence
            assert self.tiles
        else:
            self.sequence = sequence.split()
        cursor = [0, 0]  #insertion point of the tile in the matrix
        for i, word in enumerate(self.sequence):
            wl = len(word.decode('utf-8'))
            if cursor[0] + wl > self.cols:
                cursor[0] = 0
                cursor[1] += 1
            is_selected = True if i == self.selected_tile else False
            descriptor = (cursor[:], word, is_selected)
            try:
                cached_descriptor = self.tiles[i][0]
            except (NameError, IndexError):
                cached_descriptor = None
            # Modify only tiles that have changed since last arrangement
            if descriptor != cached_descriptor:
                # Create new object
                color = (255, 255, 0) if is_selected else (255, 255, 255)
                new_tile = Tile(word, matrix_x=cursor[0], matrix_y=cursor[1],
                                text_size=self.text_size, tile_color=color)
                # Insert new object
                if cached_descriptor == None:  #new tile collection altogether!
                    self.tiles.append((descriptor, new_tile))
                else:  #just a change in the collection
                    self.tiles[i] = (descriptor, new_tile)
            cursor[0] += wl
            
    def move_selection(self, direction):
        '''
        Change the selected tile of the clockface
        '''
        if direction == -1 and self.selected_tile == 0 or \
           direction == +1 and self.selected_tile == len(self.sequence)-1:
            return
        self.selected_tile += direction
        self.arrange_sequence()
        
    def shift_selected(self, direction):
        '''
        Shift the selected tile to either left or right.
        '''
        if direction == -1 and self.selected_tile == 0 or \
           direction == +1 and self.selected_tile == len(self.sequence)-1:
            return
        target_pos = self.selected_tile + direction
        swap = self.sequence[target_pos]
        self.sequence[target_pos] = self.sequence[self.selected_tile]
        self.sequence[self.selected_tile] = swap
        self.selected_tile = target_pos
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
                                (self.cols*self.text_size, self.rows*self.text_size)))
        self.scene.add(svg.Line((0, self.rows*self.text_size),
                                (self.cols*self.text_size, self.rows*self.text_size)))
        self.grid_visible=False

    def display(self):
        '''
        Display the clockface.
        '''
        self.scene.items = []
        self.draw_margins()
        for tile in self.tiles:
            self.scene.add(tile[1])
        xml = self.scene.get_xml()
        rsvg_handler = rsvg.Handle(data=xml.getvalue())
        pixbuf = rsvg_handler.get_pixbuf()
        self.image_widget.set_from_pixbuf(pixbuf)
        

def test():
    cf = ClockFace(20, 20)
    cf.arrange_sequence("I could easily span this stuff over a lot of \
    lines if I wanted to. But I am kind and I will spare you that.")
    cf.display()
    return

if __name__ == '__main__': 
    test()