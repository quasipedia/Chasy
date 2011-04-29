# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import glob
import sys
import utils

class Logic(object):
    
    '''
    Contains all the logic needed for the program to run, except the language
    specific functionality, which is given by individual clock modules.
    '''
    
    def __init__(self):
        # Imports all available clock modules, and organise a human-readable
        # list of them in the form {'human_name':imported_module_object}
        self.available_clocks = {}
        for module_name in glob.glob("clocks/*.py"):
            module_name = module_name[7:-3]
            if module_name != '__init__':
                module_name = 'clocks.' + module_name
                __import__(module_name)
                imported = sys.modules[module_name]
                human_name = getattr(imported, 'Clock').__module_name__
                self.available_clocks[human_name] = imported
        self.switch_clock('Verbose Russian')
        
    def switch_clock(self, clock_name):
        self.clock = self.available_clocks[clock_name].Clock()
    
    def get_phrases_analysis(self):
        '''
        Returns an analysis of the complete set of time sentences.
        '''
        stats = []
        phrase_list = self.clock.get_phrases_dump()
        phrase_set = set(phrase_list)
        word_set = set(' '.join(phrase_list).split())
        n_phrases = len(phrase_list)
        n_unique_phrases = len(phrase_set)
        n_unique_words = len(word_set)
        #len(unicode) would return bytesize of string, non number of chars
        n_chars = sum([len(w.decode("utf-8")) for w in word_set])
        approx_board_size = utils.get_minimum_panel_size(n_chars)
        stats.append(("Number of sentences ", n_phrases)) 
        stats.append(("Number of unique sentences ", n_unique_phrases))
        stats.append(("Number of unique words ", n_unique_words))
        stats.append(("Number of chars to be displayed ", n_chars))
        stats.append(("Minimum board size (X, Y, extra cells)", approx_board_size))
        col_width = max(map(len, [t for t, v in stats])) + 3
        for t, v in stats:
            print(t.ljust(col_width, '.') + ' %s') % str(v)
            
    def get_time_phrase(self, hours, minutes):
        return self.clock.get_time_phrase(hours, minutes)
    
