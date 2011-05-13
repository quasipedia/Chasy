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

    def __what_convert(self, what, target_format):
        '''
        Helper function used to allow to pass-in both instances of Element and
        positional indexes. Return either of the two according to 
        "target_format" parameter (that can be "index" or "element").
        '''
        if target_format not in ('index', 'element'):
            raise BaseException("target_format must be 'index' or 'element'")
        if isinstance(what, Element):
            ret = what.get_position() if target_format == 'index' else what
        elif type(what) == int:
            # Normalise negative indexes such as list[-1]
            what = what if what >= 0 else len(self)+what
            ret = self[what] if target_format == 'element' else what
        else:
            raise BaseException("Param 'what' needs to be Element() or index")
        return ret

    def get_char_length(self):
        '''
        Return the length of the entire sequence, unstripped, in # of chars.
        '''
        return sum([len(item.word.decode('utf-8')) for item in self])        

    def get_adjacent_elements(self, what):
        '''
        Return a tuple with the two elements lying to the left and right
        of the one passed as parameter.
        - what: instance of Element() or index index in SuperSeq
        '''
        ref = self.__what_convert(what, 'index')
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
        el_pos = self.__what_convert(what, 'index')
        dict_ = {}
        for el in self[el_pos+1:]:
            len = el.get_word_length(strip=True)
            try:
                dict_[len].append(el)
            except KeyError:
                dict_[len] = [el]
        return dict_

    def move_remaining_longest_next_to(self, what_or_none, 
                                       upper=None, lower=None):
        '''
        Move the longest possible word to position "position" in the sequence.
        "remaining" refers to the fact the words are taken "to the right of"
        position.
        Return True if any shift has been performed, otherwise return False.
        - what_or_none: instance of Element() or index index in SuperSeq or
          None. If None is passed in, it means "move to position 0"
        - upper, lower: the upper and lower lenght limits for words.
        '''
        target_pos = 0 if what_or_none == None else \
                          self.__what_convert(what_or_none, 'index') + 1
        print(what_or_none, target_pos, len(self))
        assert target_pos < len(self)
        candidates = self.get_remaining_elements_by_size(target_pos)
        for length, elems in sorted(candidates.items(), reverse=True):
            # Only consider elements fitting the limits.
            if upper and length > upper or lower and length < lower:
                continue
            for el in elems:
                if self.shift_element_to_position(el, target_pos):
                    # Discard results in which the shifted word cause a space
                    # to appear if this cause the line to break.
                    if upper and length == upper and \
                       self[target_pos-1].test_contact():
                        continue
                    return True
        return False

    def shift_element_to_position(self, what, target, only_if_sane=True):
        '''
        Try to shift an element to position "target". Return True on success,
        False otherwise. 
        - what: instance of Element() or index index in SuperSeq
        - only_if_sane: perform the shifting only if the resulting seq can
          still generate all the phrases.
        '''
        assert self.__what_convert(what, 'index') != target
        direction = 'right' if target > self.__what_convert(what, 'index') \
                            else 'left'
        el = self.__what_convert(what, 'element')
        moveable = True
        while moveable:
            # Need to pass "what" as "el" as index(el) will change!!
            moveable = self.shift_element(el, direction, only_if_sane)
            if el.get_position() == target:
                return True
        return False
    
    def shift_element(self, what, direction, 
                      only_if_sane=True, callback=None):
        '''
        Shift the selected element to either left or right in the positional
        order of the supersequence.
        - what: instance of Element() or index index in SuperSeq
        - direction: 'left' or 'right'
        - only_if_sane: perform the shifting only if the resulting seq can
          still generate all the phrases.
        - callback: an optional callback
        '''
        el_pos = self.__what_convert(what, 'index')
        if direction == 'left' and el_pos != 0:
            new_pos = el_pos-1
        elif direction == 'right' and el_pos != len(self):
            new_pos = el_pos+1
        else:
            raise BaseException('Shifting error! El:%s Dir:%s' %
                                (repr(el_pos), repr(direction)))
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
        if callback:
            callback()
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