# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import glob
import sys
import utils
import textwrap
import gtk
import gobject

class Logic(object):
    
    '''
    Contains all the logic needed for the program to run, except the language
    specific functionality, which is given by individual clock modules.
    '''
    
    def __init__(self, parent_menu, callback):
        # This callback is used to signal the need for a screen refresh
        self.invoke_refresh = callback
        # Imports all available clock modules and organise a human-readable
        # list of them in the form {'human_name':imported_module_object}
        self.available_modules = {}
        for module_name in glob.glob("clocks/*.py"):
            module_name = module_name[7:-3]
            if module_name != '__init__':
                module_name = 'clocks.' + module_name
                __import__(module_name)
                imported = sys.modules[module_name]
                human_name = getattr(imported, 'Clock').__module_name__
                self.available_modules[human_name] = imported
        # Populate the parent menu with modules names
        mod_menu = gtk.Menu()
        group = None
        for name in sorted(self.available_modules):
            item = gtk.RadioMenuItem(group, label=name)
            mod_menu.append(item)
            if group == None:
                group = item
                initial_module = name
            item.connect("toggled", self.switch_clock, name)
        parent_menu.set_submenu(mod_menu)
        # Pick the first module of the list to start with
        self.clock = self.available_modules[initial_module].Clock()
        group.set_active(True)
        
    def switch_clock(self, widget, clock_name):
        if widget.get_active():
            self.clock = self.available_modules[clock_name].Clock()
            try:
                self.invoke_refresh()
            except AttributeError:
                # If invoked during the __init__, the callback won't work!!
                pass
    
    def get_phrases_analysis(self):
        '''
        Returns an analysis of the complete set of time sentences.
        '''
        stats = []
        phrase_list = self.clock.get_phrases_dump()
        phrase_set = set(phrase_list)
        word_set = set(' '.join(phrase_list).split())

        stats.append(("SENTENCES", ''))
        n_phrases = len(phrase_list)
        stats.append(("Number of sentences", n_phrases)) 
        n_unique_phrases = len(phrase_set)
        stats.append(("Number of unique sentences", n_unique_phrases))

        stats.append(("WORDS", ''))
        n_unique_words = len(word_set)
        stats.append(("Number of unique words", n_unique_words))
        words_per_sentence = utils.get_min_avg_max(phrase_set, 'words')
        stats.append(("Words per sentence (min, avg, max)", 
                      words_per_sentence))
        
        stats.append(("CHARS", ''))
        #len(unicode) would return bytesize of string, non number of chars
        n_chars = sum([len(w.decode("utf-8")) for w in word_set])
        stats.append(("Chars in unique words", n_chars))
        chars_per_word = utils.get_min_avg_max(word_set, 'chars')
        stats.append(("Chars per word (min, avg, max)", chars_per_word))
        chars_per_sentence = utils.get_min_avg_max(phrase_set, 'chars')
        stats.append(("Chars per sentence (min, avg, max)", chars_per_sentence))

        stats.append(("MATRIX SIZE", ''))        
        approx_board_size = utils.get_minimum_panel_size(n_chars)
        stats.append(("Minimum board size (X, Y, extra cells)", 
                      approx_board_size))

        # Generate text data
        col_width = max(map(len, [t for t, v in stats])) + 7
        for t, v in stats:
            if v != '':
                t += ' '
                print(t.ljust(col_width, '.') + ' %s') % str(v)
            else:
                t = ' ' + t
                print(t.rjust(col_width, '>'))
        
        # Append disclaimer
        disclaimer = '''\
        Be aware that the board size indicated here is to
        be considered as an "hard bottom limit" below which is physically
        impossible to go. However it is possible that the actual matrix will 
        need to be larger to accommodate for logical and spatial needs.'''
        print('\n' + textwrap.fill(textwrap.dedent(disclaimer), col_width))
            
    def get_time_phrase(self, hours, minutes):
        return self.clock.get_time_phrase(hours, minutes)
    
