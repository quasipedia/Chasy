#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import gtk
import imp
import utils
import difflib
from utils import debug

class Logic(object):
    
    '''
    Contains all the logic needed for the program to run, except the language
    specific ones, which are given by individual modules.
    '''
    
    def __init__(self, clock=None):
        # Dynamically import the desired module
        if clock is not None:
            clock_module = imp.load_source(clock, 'clocks/' + clock + '.py')
            self.clock = clock_module.Russian()
    
    def test_order_on_rules(self, order, rules):
        '''
        Test if a given order of words is compliant with all the topographic
        rules needed to formulate time sentences (phrases).
        Uses a ruleset to perform the test.
        '''
        for word in order:
            rule = rules[word]
            r_index = utils.list_rindex(order, word)
            l_index = order.index(word)
            if order.count(word) < rule['min_rep']:
                return False
            if not rule['right_of'].issubset(order[:r_index]):
                return False
            if not rule['left_of'].issubset(order[l_index+1:]):
                return False
        return True
    
    def test_order_on_phrases(self, order, phrases):
        '''
        Test if a given order of words is compliant with all the topographic
        rules needed to formulate time sentences (phrases).
        Uses the actual phrases to perform the test.
        '''
        for phrase in phrases:
            cursor = 0
            for word in phrase:
                try:
                    cursor += order[cursor:].index(word) 
                except ValueError as msg:
                    return False
        return True
    
    def get_dump(self, with_numbers=False):
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
        phrase_list = self.get_dump()
        phrase_set = set(phrase_list)
        word_set = set(' '.join(phrase_list).split())
        n_phrases = len(phrase_list)
        n_unique_phrases = len(phrase_set)
        n_unique_words = len(word_set)
        n_chars = sum([len(w) for w in word_set])
        approx_board_size = utils.get_minimum_panel_size(n_chars)
        stats.append(("Number of sentences ", n_phrases)) 
        stats.append(("Number of unique sentences ", n_unique_phrases))
        stats.append(("Number of unique words ", n_unique_words))
        stats.append(("Number of chars to be displayed ", n_chars))
        stats.append(("Minimum square size ", approx_board_size))
        col_width = max(map(len, [t for t, v in stats])) + 3
        for t, v in stats:
            print(t.ljust(col_width, '.') + ' %s') % str(v)
    
    def get_order_rules(self, phrase_list):
        '''
        Returns the order rules for every unique word in the list of time
        phrases. For each word in the pool it is returned: 
        - how many repetitions of it can be in the same sentence
        - what words to be to the left of it
        - what words to be to the right of it
        '''
        # Initialisation
        phrase_set = set(phrase_list)
        word_set = set(' '.join(phrase_list).split())
        order_rules = {}
        for word in word_set:
            order_rules[word] = {'min_rep':0, 
                                 'right_of':set(), 
                                 'left_of':set()}
        for phrase in phrase_set:
            words = phrase.split()
            for word in words:
                # Update max repetitions count if necessary
                rep = words.count(word)
                if rep > order_rules[word]['min_rep']:
                    order_rules[word]['min_rep'] = rep
                # Add rules for left_of - ignore duplicates of self
                for lo in words[words.index(word)+1:]:
                    if lo != word:
                        order_rules[word]['left_of'].add(lo)
                # Add rules for right_of - ignore duplicates of self
                # the slicing below is equivalent to "rindex" on strings
                for ro in words[:utils.list_rindex(words, word)]:
                    if ro != word:
                        order_rules[word]['right_of'].add(ro)
        return order_rules
    
    def get_order(self, order_rules):
        '''
        Return one of the possible orders of the word set so that all time 
        sentences can be created with their words in the correct order.
        '''
        # Check if there are other conditions but plain repetition of a
        # word in a sentence, that make duplicating a word indispensable
        debug()
        duplicates = []
        for w in order_rules:
            debug(w, order_rules[w])
            known_reps = order_rules[w]['min_rep'] 
            if known_reps > 1:
                for i in range(known_reps-1):
                    duplicates.append(w)
        circular_references = {}
        for w in order_rules:
            dups = order_rules[w]['left_of'].\
                   intersection(order_rules[w]['right_of'])
            if len(dups) != 0 and w not in duplicates:
                circular_references[w] = dups
        debug('CR:', circular_references)
        # Creates new duplicates to overcome circular references.
        # There might be several ways to resolve circular references, the
        # programs starts by duplicating those words with the highest number
        # of conflicting topological condistions.
        if len(circular_references) > 0:
            cr_per_word = sorted([(k, len(circular_references[k])) \
                          for k in circular_references])
            index = 0
            while len(circular_references) > 0:
                dup_word = cr_per_word[index][0]
                duplicates.append(dup_word)
                del circular_references[dup_word]
                # the following line is needed as it's not possible to change
                # the size of a dict during iteration on it
                keys = [k for k in circular_references]
                for k in keys:
                    circular_references[k].discard(dup_word)
                    if len(circular_references[k]) == 0:
                        del circular_references[k]   
                index += 1     
        # Create order with bubble sorting     
        order = [w for w in order_rules] + duplicates
        while True:
            changed = False
            for index in range(len(order)-1):
                a = order[index]
                b = order[index+1]
                # if they are identical words, there is no point swapping them
                if a == b:
                    continue
                # if in the wrong place, swap
                if a not in order_rules[b]['right_of']:
                    order[index] = b 
                    order[index+1] = a
                    changed = True
                # if in the right place, check for duplicates
                elif a in order_rules[b]['left_of']:
                    # find the rightmost duplicate and if too much to the left,
                    # move it right at the right of "b"
                    dup_index = utils.list_rindex(order, b)
                    if dup_index < index+1:
                        # "index+1" instead of "index+2" because popping the 
                        # item will scale all items to the left of 1 unit
                        order.insert(index+1, order.pop(dup_index))
                        changed = True
            if not changed:
                break
        debug('ORDER', order)
        return order
    
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
        self.cyrillic = self.builder.get_object("cyrillic")
        
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
        self.dump_buffer.set_text('\n'.join(self.logic.get_dump(True)))
        self.dump_window.show()

    def on_dump_textonly_activate(self, widget):
        self.dump_buffer.set_text('\n'.join(self.logic.get_dump(False)))
        self.dump_window.show()

    def on_dump_encoded_activate(self, widget):
        self.dump_buffer.set_text("Encoded")
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
        self.cyrillic.set_text(phrase)

if __name__ == '__main__':
    Gui('russian')
    gtk.main()
    