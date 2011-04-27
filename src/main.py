#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import gtk
import imp
import utils
from utils import debug

class Logic(object):
    
    '''
    Contains all the logic needed for the program to run, except the language
    specific functionality, which is given by individual clock modules.
    '''
    
    def __init__(self, clock=None):
        # Dynamically import the desired module
        if clock is not None:
            clock_module = imp.load_source(clock, 'clocks/' + clock + '.py')
            self.clock = clock_module.Russian()
    
    def get_phrases_dump(self, with_numbers=False):
        '''
        Generate the dump of all the time phrases in a day (1440 for a minute-
        accurate clock). If 'with_numbers' is True, prepend a numeric 
        representation of the time in the form HH:MM.
        '''
        phrases = []
        for h in range(24):
            for m in range(60):
                phrase = ''
                if with_numbers == True:
                    phrase += str(h).zfill(2) + ':' + str(m).zfill(2) + '  '
                phrases.append(phrase + self.clock.get_text(h, m))
        return phrases
    
    def get_phrases_analysis(self):
        '''
        Returns an analysis of the complete set of time sentences.
        '''
        stats = []
        phrase_list = self.get_phrases_dump()
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
    
    def get_words_sequence(self, phrases=None):
        '''
        Return a common supersequence to all the phrases.
        The generation of the supersequence is done heuristically and there is
        no guarantee the supersequence will be the shortest possible.
        If no phrases are passed as parameters, all the phrases for the
        currently active clock module will be used (so the supersequence will
        be able to display the entire day on the clock). 
        '''
        # 0. Generate a list of unique words
        debug()
        if phrases == None:
            phrases = self.get_phrases_dump()
        words = set()
        for phrase in phrases:
            for word in phrase.split():
                words.add(word)
        # 1. Convert all words to 1-char-long symbols (words are unmodifiable)
        #    and encode the phrases accordingly
        symbol_to_word = {}
        word_to_symbol = {}
        for i, word in enumerate(words):
            # 33 (!) is the first printable char and is saved for later use
            symbol = unichr(34 + i)
            symbol_to_word[symbol] = word
            word_to_symbol[word] = symbol
        codes = utils.convert(word_to_symbol, phrases)
        # 2. Group all sentences in "families" of similar sentences
        groups = utils.group_similar_phrases(codes)
        for group in groups:
            debug(utils.convert(symbol_to_word, group))
        # Group together sentences with the same subsequence pattern
        
        # 2b. Start by the closest pair and find the longest common subsequence
        # 2c. Add to the family until the original LCS can be used as the
        #     common base between the family and the new sentence.
        # 2d. Restart from 2a until all possible families have been generated.
        # 3. Generate the sequence that contains all family members
        # 4. Find the common sequence between all family sequences
        # 5. Re-convert symbols into words
        return []
    
    def test_sequence_against_phrases(self, sequence, phrases):
        '''
        Test if a given sequence of words can be used to generate all the 
        time phrases. Return True for passed.
        '''
        for phrase in phrases:
            cursor = 0
            for word in phrase:
                try:
                    cursor += sequence[cursor:].index(word) 
                except ValueError:
                    return False
        return True
    
    def get_text(self, hours, minutes):
        '''
        Wrapper for the clock-specific logic
        '''
        return self.clock.get_text(hours, minutes)


class Gui(object):

    '''
    Provide the visual environment for interacting with the boat from the PC.
    '''

    def __init__(self, clock):
        
        self.logic = Logic(clock)
        self.gui_file = "../data/gui.xml"
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gui_file)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window")
        self.dump_window = self.builder.get_object("dump_window")
        self.dump_buffer = self.builder.get_object("dump_buffer")
        self.about_dialogue = self.builder.get_object("about_dialogue")
        self.output_text = self.builder.get_object("output_text")
        
        self.hours = 0
        self.minutes = 0
        self.update_text()
        
        self.window.show_all()
        
    ###### INPUT FOR TESTING TIMES #####
        
    def on_hours_value_changed(self, widget):
        self.hours = int(widget.get_text())
        self.update_text()
        
    def on_minutes_value_changed(self, widget):
        self.minutes = int(widget.get_text())
        self.update_text()
        
    ##### MENU COMMANDS ######    
    
    def on_dump_full_activate(self, widget):
        self.dump_buffer.set_text('\n'.join(self.logic.get_phrases_dump(True)))
        self.dump_window.show()

    def on_dump_textonly_activate(self, widget):
        self.dump_buffer.set_text('\n'.join(self.logic.get_phrases_dump()))
        self.dump_window.show()

    def on_analysis_word_stats_activate(self, widget):
        self.logic.get_phrases_analysis()
    
    ##### WINDOWS MANAGEMENT #####
        
    def on_close_dump_button_clicked(self, widget):
        self.dump_window.hide()

    def on_dump_window_delete_event(self, widget, data):
        self.dump_window.hide()
        return True #prevent destruction

    def on_about_select(self, widget):
        self.about_dialogue.show()

    def on_about_dialogue_delete_event(self, widget):
        self.about_dialogue.hide()
        return True

    def on_about_dialogue_response(self, widget, data):
        self.about_dialogue.hide()

    def on_window_destroy(self, widget):
        gtk.main_quit()
        
    def update_text(self):
        phrase = self.logic.get_text(self.hours, self.minutes)
        self.output_text.set_text(phrase)

if __name__ == '__main__':
    l = Logic('russian')
    phrases = ['it is five past one',
               'it is one to two',
               'it is two to three',
               'it is three to four',
               'it is four to five',
               'it is five to six',
               'it is four past seven',
               'it is three past eight',
               'it is two past nine',
               'it is one past ten',
               "it is eleven o'clock",
               "it is twelve o'clock",
               "it is one o'clock",
               "it is two o'clock",
               "it is three o'clock",
               ]
    l.get_words_sequence(phrases)
#    Gui('russian')
#    gtk.main()
    