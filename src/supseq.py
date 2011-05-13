#!/usr/bin/env python
# -*- coding: utf-8  -*-
'''
Allows manipulation and control of a time phrases supersequence.

A big part of a large word clock desing is about finding the shortest 
supersequence of words that will allow to reproduce all the time phrases
that the clock needs to display.

This module provide a supersequence class with methods for its manipulation,
storage, modification, testing, etc... 
'''

#import  modules_names_here

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Element(object):
    
    '''
    Logical representation of an element in the supersequence.
    '''

    def __init__(self, sequence, word):
        self.sequence = sequence
        self.word = word.decode('utf-8')
        self.tile = None  # this is just a reminder, see ClockFace!

    def get_position(self):
        '''
        Simulate introspective behaviour for the position of an element
        into the sequence containing it.
        '''
        for i, el in enumerate(self.sequence):
            if el == self:
                return i
        raise BaseException('Element is not part of the sequence')
    
    def get_word_length(self, strip=False):
        '''
        Return the length of the word in number of chars to be displayed.
        '''
        word = self.word if strip == False else self.word.strip()
        return len(word.decode('utf-8'))
    
    def test_contact(self):
        '''
        Return True if there is at least one sentence in the supersequence's
        sanity pool in which the element following 'self' in the supersequence
        is used [this whould mean that the two words need spacing if they are
        on the same line on the clockface].
        '''
        pos = self.get_position()
        if pos == len(self.sequence) - 1:  #if last in the sequence
            return False
        str_to_check = self.word + ' ' + self.sequence[pos + 1].word
        for phrase in self.sequence.sanity_pool:
            if str_to_check in phrase:
                return True
        return False
        

class SuperSequence(list):
    
    '''
    Logical representation of a supersequence as a collection of element 
    objects.
    '''
    
    def __init__(self, sequence, sanity_pool):
        '''
        - sequence, string: supersequence of words
        - sanity_pool: list of sentences the sequence should be used for.
        '''
        for text in sequence.split():
            self.append(Element(self, text))
        self.sanity_pool = sanity_pool[:]  # prevent modification of original

    def get_length(self):
        '''
        Return the length of the entire sequence, unstripped, in # of chars.
        '''
        return sum([len(item.word.decode('utf-8')) for item in self])        

    def get_adjacent_elements(self, element):
        '''
        Return a tuple with the two elements lying to the left and right
        of the one passed as parameter.
        '''
        ref = element.get_position()
        left = None if ref == 0 else self[ref-1] 
        right = None if ref == len(self) else self[ref+1] 
        return (left, right)
    
    def get_sequence_as_string(self):
        '''
        Return unicode representation of sequence.
        '''
        return ' '.join([el.word for el in self])
    
    def get_remaining_elements_by_size(self, what):
        '''
        Return a dictionary in the form word_length:list_of_elements of all
        the elements whose position is right of element indicated by what.
        - what: instance of Element() or index index in SuperSeq
        '''
        if isinstance(what, Element):
            el_pos = what.get_position()
        elif type(what) == int:
            el_pos = what
        else:
            raise BaseException("Param 'what' needs to be Element() or index")
        dict_ = {}
        for el in self[el_pos+1:]:
            len = el.get_word_length(strip=True)
            try:
                dict_[len].append(el)
            except KeyError:
                dict_[len] = [el]
        return dict_
    
    def shift_element(self, what, direction, only_if_sane=True):
        '''
        Shift the selected element to either left or right in the positional
        order of the supersequence.
        - what: instance of Element() or index index in SuperSeq
        - direction: 'left' or 'right'
        '''
        if isinstance(what, Element):
            el_pos = what.get_position()
        elif type(what) == int:
            el_pos = what
        else:
            raise BaseException("Param 'what' needs to be Element() or index")
        if direction == 'left' and el_pos != 0:
            new_pos = el_pos-1
        elif direction == 'right' and el_pos != len(self):
            new_pos = el_pos+1
        else:
            raise BaseException('Shifting error! El:%s Dir:%s' %
                                (repr(what), repr(direction)))
        if only_if_sane:
            # Stage the change and verify the result is still sane...
            new_seq = SuperSequence(self.get_sequence_as_string(), 
                                    self.sanity_pool)
            new_seq[el_pos], new_seq[new_pos] = \
                                    new_seq[new_pos], new_seq[el_pos]
            # ...if not, return
            if not new_seq.sanity_check():
                return False
        # Strip potential spaces introduced for clockface reasons...
        self[el_pos].word = self[el_pos].word.strip()
        self[new_pos].word = self[new_pos].word.strip()
        # ...and swap!
        self[el_pos], self[new_pos] = self[new_pos], self[el_pos]
        return True

    def sanity_check(self, phrases=None):
        '''
        Test if the sequence can be used to generate all phrases.
        - phrases: list of strings or None. If None, check against all the 
                   phrases given at time of sequence generation.
        Return True if sequence is sane, False otherwise
        '''
        if not phrases:
            phrases = self.sanity_pool
        word_sequence = self.get_sequence_as_string().split()
        for phrase in phrases:
            cursor = 0
            for word in phrase.split():
                try:
                    # Following strip is for added spaces from clockface
                    cursor += word_sequence[cursor:].index(word.strip()) + 1
                except ValueError:
                    return False
        return True


def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()