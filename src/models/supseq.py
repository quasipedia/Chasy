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

import copy
import math

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
        # Cache of elements that can block shifting in either direction
        self.blocked_by = {'left':[], 'right':[]}
        self.tile = None  # this is just a reminder, see ClockFace!
        self.led_strings = None

    def get_position(self):
        '''
        Simulate introspective behaviour for the position of an element
        into the sequence containing it.
        '''
        for i, el in enumerate(self.sequence):
            if el == self:
                return i
        raise BaseException('Element \'%s\' is not part of the sequence'
                            % self.word)

    def get_word_length(self, strip=None):
        '''
        Return the length of the word in number of chars to be displayed.
        - strip: None, 'left', 'right', 'both'
        '''
        if strip == None:
            word = self.word
        elif strip == 'left':
            word = self.word.lstrip()
        elif strip == 'right':
            word = self.word.rstrip()
        elif strip == 'both':
            word = self.word.strip()
        else:
            raise BaseException('Wrong strip parameter')
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
        str_to_check = self.word.strip() + ' ' + \
                       self.sequence[pos + 1].word.strip()
        for phrase in self.sequence.sanity_pool:
            if str_to_check in phrase:
                return True
        return False


class SuperSequence(list):

    '''
    Logical representation of a supersequence as a collection of element
    objects. Inherits from a list class.
    '''

    def __init__(self, sequence, sanity_pool):
        '''
        - sequence, string: supersequence of words
        - sanity_pool: list of sentences the sequence should be used for.
        '''
        for text in sequence.split():
            self.append(Element(self, text))
        self.sanity_pool = sanity_pool[:]  # prevent modification of original
        self._merged_mapping = {}  # needed if merging optimisation is used

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

    def __force_merge_and_check(self, pos_large, pos_small):
        '''
        This is a DANGEROUS method. It merges two words in one, WHITOUT ANY
        KIND OF CHECK on the sensibility of the action. Only after the merge
        is done (and NOT REVERSIBLE), check that the sequence is still sane.
        [This method is thought to be used on cloned, disposable sequences,
        this is why the elements are passed positionally and not as object
        reference]
        '''
        # self._merged_mapping is a dictionary indicating into what words
        # [w1, w2, w3, w4...] an original word w0 has been merged.
        # The format is self._merged_mapping[w0] = [w1, w2, w3, w4...]
        large = self[pos_large]
        small = self[pos_small]
        try:
            self._merged_mapping[small.word].append(large.word)
        except KeyError:
            self._merged_mapping[small.word] = [large.word]
        self.pop(pos_small)
        return self.sanity_check()

    def _closest_next_match(self, sequence, word):
        '''
        Helper method that returns the first match of "word" in "sequence",
        choosing - where applicable - between the word "as it is" or any of
        its mapped representations.
        '''
        hits = []
        to_try = [word]
        try:
            to_try += self._merged_mapping[word]
        except KeyError:  #no mapping for this word
            pass
        for w in to_try:
            try:
                hits.append(sequence.index(w))
            except ValueError:
                pass
        return None if hits == [] else min(hits)

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
                    # Following strip() is for added spaces from clockface
                    cursor += self._closest_next_match(word_sequence[cursor:],
                                                        word.strip()) + 1
                except TypeError:  #Triggered by "cursor += None" operation
                    return False
        return True

    def get_sequence_as_string(self):
        '''
        Return unicode representation of sequence.
        '''
        return ' '.join([el.word.strip() for el in self])

    def get_char_length(self):
        '''
        Return the length of the entire sequence, unstripped, in # of chars.
        '''
        return sum([item.get_word_length() for item in self])

    def get_lenght_shortest_elem(self):
        '''
        Return the stripped length of the shortest word in the sequence.
        '''
        return min([item.get_word_length(strip='both') for item in self])

    def get_lenght_longest_elem(self):
        '''
        Return the stripped length of the shortest word in the sequence.
        '''
        return max([item.get_word_length(strip='both') for item in self])

    def get_duplicate_words(self):
        '''
        Return a list of duplicate words in a sequence.
        '''
        word_list = self.get_sequence_as_string().split()
        word_set = set(word_list)
        duplicates = []
        for word in word_set:
            if word_list.count(word) > 1:
                duplicates.append(word)
        return duplicates

    def get_adjacent_elements(self, what):
        '''
        Return a tuple with the two elements lying to the left and right
        of the one passed as parameter.
        - what: instance of Element() or index in SuperSeq
        '''
        ref = self.__what_convert(what, 'index')
        left = None if ref == 0 else self[ref-1]
        right = None if ref == len(self) else self[ref+1]
        return (left, right)

    def get_remaining_elements_by_size(self, what=None):
        '''
        Return a list of elements right of "what" decreasingly ordered by
        word length. If no "what" element is given, the entire sequence is
        processed.
        - what: instance of Element() or index index in SuperSeq.
        '''
        if what == None:
            el_pos = 0
        else:
            el_pos = self.__what_convert(what, 'index')
        return sorted(self[el_pos:],
                      key = lambda x: x.get_word_length(),
                      reverse=True)

    def shift_element(self, what, direction,
                      only_if_sane=True, callback=None):
        '''
        Shift the selected element to either left or right in the positional
        order of the supersequence.
        - what: instance of Element() or index in SuperSeq
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
            scrap = copy.deepcopy(self)
            scrap[el_pos], scrap[new_pos] = scrap[new_pos], scrap[el_pos]
            # ...if not, return
            if not scrap.sanity_check():
                el = self.__what_convert(what, 'element')
                el.blocked_by[direction].append(self[new_pos])
                return False
        # Strip potential spaces introduced for clockface reasons...
        self[el_pos].word = self[el_pos].word.strip()
        self[new_pos].word = self[new_pos].word.strip()
        # ...and swap!
        self[el_pos], self[new_pos] = self[new_pos], self[el_pos]
        if callback:
            callback()
        return True

    def shift_element_to_position(self, what, target, only_if_sane=True):
        '''
        Try to shift an element to position "target". Return True on success,
        False otherwise. NOTE!!! 'self' get modified by the attempt, and the
        word gets shifted as much as possible towards it's target destination.
        - what: instance of Element() or index in SuperSeq
        - only_if_sane: perform the shifting only if the resulting seq can
          still generate all the phrases.
        '''
        # The shift is a no-move!
        if self.__what_convert(what, 'index') == target:
            return True
        # Look up cache first!
        el = self.__what_convert(what, 'element')
        el_pos = self.__what_convert(what, 'index')
        direction = 'right' if target > el_pos else 'left'
        start_, stop_ = sorted([el_pos, target])
        if set(self[start_:stop_]).intersection(set(el.blocked_by[direction])):
            return False
        # Try to actually shift the element
        moveable = True
        while moveable:
            # Need to pass "what" as "el" as index(el) will change!!
            moveable = self.shift_element(el, direction, only_if_sane)
            if el.get_position() == target:
                return True
        return False

    def shift_remaining_longest_next_to(self, what_or_none, max_len=None):
        '''
        Move the longest possible word to position "position" in the sequence.
        "remaining" refers to the fact the words are taken "to the right of"
        position.
        Return the element that has been shifted or False if no shift resulted
        in an element ending up next to the target.
        - what_or_none: instance of Element() or index in SuperSeq or
          None. If None is passed in, it means "move to position 0"
        - max_len: the upper lenght limit for the word.
        '''
        target_pos = 0 if what_or_none == None else \
                          self.__what_convert(what_or_none, 'index') + 1
        assert target_pos < len(self)
        candidates = self.get_remaining_elements_by_size(target_pos)
        for el in candidates:
            el_length = el.get_word_length(strip='both')
            # Only consider elements fitting the limits.
            if max_len and el_length > max_len:
                continue
            if self.shift_element_to_position(el, target_pos):
                # Discard results in which the shifted word cause a space
                # to appear if this cause the line to break.
                if max_len and el_length == max_len and \
                   self[target_pos-1].test_contact():
                    continue
                return el
        return False

    def converge_elements(self, one, two):
        '''
        Makes two elements to converge as far as possible. Return True if
        they reached two adjacent positions, False otherwise.
        - one, two: instances of Element() or indexes in SuperSeq
        '''
        one = self.__what_convert(one, 'element')
        two = self.__what_convert(two, 'element')
        # Sort elements according to their order in the sequence
        one, two = sorted([one, two], key = lambda x: x.get_position())
        while True:
            # if they have converged
            if two.get_position() - one.get_position() == 1:
                return True
            # Smartass trick: the logic "or" guarantees that only either e1 or e2
            # get shifted at each pass [if the first shift returns True, the
            # if condition is already True and the second shift is neither tried.
            if not (self.shift_element(one, 'right') or \
                   self.shift_element(two, 'left')):
                return False

    def eliminate_redundancies(self, callback=None):
        '''
        Eliminate redundant words by checking if they can converge next to
        each other, and then if one of them can be eliminated.
        - callback is the function to invoke to update progress data in GUI
        '''
        dup_words = self.get_duplicate_words()
        for word in dup_words:
            # Find all elements representing an instance of that word
            dup_els = []
            for el in self:
                if el.word == word:
                    dup_els.append(el)
            # Then try to make them converge
            for i in range(len(dup_els)-1):
                if callback:
                    callback()
                e1 = dup_els[i]
                e2 = dup_els[i+1]
                # if they converged
                if self.converge_elements(e1, e2):
                    guinea_pig = copy.deepcopy(self)
                    guinea_pig.pop(e1.get_position())
                    if guinea_pig.sanity_check():
                        self.pop(e1.get_position())
                        break
                    else:
                        break

    def get_containing_pairs(self):
        '''
        Return a list of tuples (containing_string, contained_string).
        '''
        decreasing = self.get_remaining_elements_by_size()
        matches = []
        for i, large in enumerate(decreasing):
            for small in decreasing[i+1:]:
                sws = small.word.strip()
                lws = large.word.strip()
                if sws != lws and sws in lws:
                    matches.append([large, small])
        return matches

    def merge_elements(self, one, two):
        '''
        Return True if the two elements can be safely (still generating all
        sentences) merged in one. Return False othewise.
        - one, two: instances of supseq.Element
        '''
        if self.converge_elements(one, two):
            scrap = copy.deepcopy(self)
            pos_one = one.get_position()
            pos_two = two.get_position()
            if scrap.__force_merge_and_check(pos_one, pos_two):
                merge_result = self.__force_merge_and_check(pos_one, pos_two)
                assert merge_result == True
                return True
        return False

    def substring_merging_optimisation(self, callback=None):
        '''
        Try to merge together two words if one is a substring of the other.
        Typical example: 'five' and 'twenty-five' or 'eight' and 'eighteen'.
        '''
        self.halt_heuristic = False
        if callback:
            callback(phase='Substring merging', time='---', bar=0)
        merged_objects = []
        pairs = self.get_containing_pairs()
        for one, two in pairs:
            if self.halt_heuristic == True:
                return
            if callback:
                callback()
            print("W1-> %s  W2-> %s" % (one.word, two.word))
            if two in merged_objects:
                print('already merged')
                continue
            if self.merge_elements(one, two):
                print('merged!')
                merged_objects.append(two)
            else:
                print('unmergeable')

    def get_best_fit(self, size, from_, new_line=False, callback=None):
        '''
        Return the list of elements that fit "size" characters in the better
        possible way. Uses only elements from the self[from_:] part of the
        sequence.
        - new_line: if True, omit the check for insertion of whitespaces before
          newly shifted word.
        - callback: a callback to be called every time an element get shifted
          (useful for gtk screen refresh)
        '''
        # This is a recursive method that returns a tuple in the form
        # (length of best fit found, [el1, el2, el3...])
        closest = [None, None]
        for el in self.get_remaining_elements_by_size(from_):
            # If el is too big, skip
            if el.get_word_length(strip='both') > size:
                continue
            # If el can't be moved, skip
            if self.shift_element_to_position(el, from_) == False:
                continue
            # The code below gets executed on successful shift only!
            # Run callback if present (typically: refresh screen)
            if callback:
                callback()
            taken_space = el.get_word_length(strip='both')
            if not new_line:
                if self[from_-1].test_contact():
                    taken_space += 1
            # If el filled the space snuggly
            if taken_space == size:
                # If spaces have to be avoided, and solution has spaces,
                # flag the solution with False even if it is snug!
                return [True, el]
            # If the added whitespace pushed the word over the end of the board
            elif taken_space > size:
                continue
            # Otherwise recurse!
            new_size = size - taken_space
            next_step = self.get_best_fit(new_size, from_+1)
            # Helper function
            how_long = lambda x: 0 if x == [None] else \
                                 sum(el.get_word_length() for el in x)
            if next_step[0] == True:  #perfect fit downstream!
                closest = [True, el] + next_step[1:]  #pass it upstream!
                return closest
            elif next_step[0] == False:  #not perfect but a fit nevertheless
                # Keep track of the best fit so far
                if new_size + how_long(next_step[1:]) > how_long(closest[1:]):
                    closest = [False, el] + next_step[1:]
            else:  #no fit at all must be the only other possibility!
                assert next_step[0] == None
                if closest == [None, None]:
                    closest = [False, el]
        # If one has ran out of elements but hasn't find a solution,
        # return the element that filled the space better
        return closest

    def set_led_strings(self):
        '''
        Assign to each element of the sequence the right led string number
        '''
        # TODO: This will need deep changes for substring optimisation
        max_led_number = 7  #TODO: put this in an interactive menu
        string_counter = 0
        for el in self:
            el.led_strings = []
            l = el.get_word_length('both')
            for s in range(int(math.ceil(l*1.0/max_led_number))):
                el.led_strings.append(string_counter)
                string_counter += 1
                # TODO: This hardcoded way of using only 15 channels per TLC
                # should be automatised to maximise energy dissipation spread
                if (string_counter + 1) % 16 == 0:
                    string_counter += 1
        self.number_of_led_strings = string_counter

        # Output a human-readable mapping of words to led strings
        text = 'LED STRING MAPPING\n'
        text += '==================\n'
        for el in self:
            row = []
            row.append(el.word.strip().ljust(15))
            for s in el.led_strings:
                row.append(str(s).zfill(3))
            text += ' '.join(row)
            text += '\n'
        text += '\n'

        # Output the noisiest combination of strings for each TLC.
        # NOISIEST = highest dissipation within TLC specifications at
        # 50% duty cycle.
        text += 'NOISIEST COMBOS\n'
        text += '===============\n'
        # Groups strings by chip, storing length
        chips_image = {}
        for el in self:
            for s in el.led_strings:
                chip_number = (s+1)/16
                tmp = el.get_word_length(strip='both')
                leds_in_string =  tmp/len(el.led_strings)  #approximate!
                try:
                    chips_image[chip_number].append((s, leds_in_string))
                except KeyError:
                    chips_image[chip_number] = [(s, leds_in_string)]
        # Calculating dissipations
        LED_INPUT_V = 24.0  #volts
        LED_DROP_V = 3.25  #volts
        CURRENT = 0.021  #amperes
        BASE_DISSIPATION = 0.060  #watts
        MAX_CHIP_DISSIPATION = 1.053  #watts
        DOT_CORRECTION = 63/63.0
        MAX_GS_VALUE = 4095
        DUTY_CYCLE = MAX_GS_VALUE/float(MAX_GS_VALUE)
        max_ch_dissipation = lambda leds : (LED_INPUT_V - leds * LED_DROP_V) \
                                            * CURRENT * DOT_CORRECTION \
                                            * DUTY_CYCLE
        # Calculate the sum of max channel dissipations for each chip
        chip_max_dissipations = [sum([max_ch_dissipation(leds) for \
                                 ch, leds in values]) for \
                                 values in chips_image.values()]
        # Calculate the max possible GS scale value for each chip.
        get_gs = lambda diss : int(round(MAX_GS_VALUE*(MAX_CHIP_DISSIPATION\
                                                       -BASE_DISSIPATION)\
                                                       /diss))
        chip_max_GS = [get_gs(diss) for diss in chip_max_dissipations]
        text += str(chip_max_GS) + '\n'
        text += '\n'


#        text += 'ASM CODE\n'
#        text += '========\n'
#        byte_counter = 0
#        for phrase in self.sanity_pool:
#            text += ';; %s\n' % phrase  # Phrase as ASM comment
#            strings = []
#            cursor = 0
#            for phrase_word in phrase.split():
#                for el in self[cursor:]:
#                    cursor += 1
#                    cface_word = el.word.strip()
#                    if phrase_word == cface_word:
#                        for s in el.led_strings:
#                            strings.append(s)
#                            byte_counter += 1
#                        break
#            # Add stop-bit information to the last string
#            strings[-1] |= 0b10000000
#            for string in strings:
#                text += '.byte %s\n' % str(string).zfill(3)
#        text += '\nRequired bytes for complete mapping: %d' % byte_counter

        text += 'C CODE\n'
        text += '========\n'
        text += 'unsigned char clockTable[] PROGMEM {\n'
        byte_counter = 0
        for phrase in self.sanity_pool:
            text += '    // %s\n' % phrase  # Phrase as ASM comment
            strings = []
            cursor = 0
            for phrase_word in phrase.split():
                for el in self[cursor:]:
                    cursor += 1
                    cface_word = el.word.strip()
                    if phrase_word == cface_word:
                        for s in el.led_strings:
                            strings.append(s)
                            byte_counter += 1
                        break
            # Add stop-bit information to the last string
            strings[-1] |= 0b10000000
#            text += '    %s,\n' % ', '.join([str(s).zfill(3) for s in strings])
            text += '    %s,\n' % ', '.join([str(hex(s)) for s in strings])
        text += '}\n'
        text += '\nRequired bytes for complete mapping: %d' % byte_counter
########### OLD BITMASK CODE ####################
#        bytes_number = self.number_of_led_strings // 8 + 1
#        for phrase in self.sanity_pool:
#            text += ';; %s\n' % phrase  # Phrase as ASM comment
#            # Raw bitmask
#            bits = ''
#            cursor = 0
#            for phrase_word in phrase.split():
#                for el in self[cursor:]:
#                    strings_number = len(el.led_strings)
#                    cursor += 1
#                    cface_word = el.word.strip()
#                    if phrase_word == cface_word:
#                        bits += '1' * strings_number
#                        break
#                    else:
#                        bits += '0' * strings_number
#            bits = bits.ljust(bytes_number*8, '0')
#            # ASM-Formatted bitmask
#            bits = list(bits)
#            bytes = ['.byte ' + ''.join(bits[i*8:i*8+8]) \
#                     for i in range(bytes_number)]
#            text += '\n'.join(bytes) + '\n'

        return text



def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()