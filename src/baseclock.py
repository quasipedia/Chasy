# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import utils

class Clock(object):
        
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
                phrases.append(phrase + self.get_time_phrase(h, m))
        return phrases
    
    def get_sequence(self, phrases=None):
        '''
        Return a common supersequence to all the phrases.
        The generation of the supersequence is done heuristically and there is
        no guarantee the supersequence will be the shortest possible.
        If no phrases are passed as parameters, all the phrases for the
        currently active clock module will be used (so the supersequence will
        be able to display the entire day on the clock). 
        '''
        # 2. Group all sentences in "families" of similar sentences
        groups = utils.group_similar_phrases(phrases)
        utils.debug(*groups)
        for phrase_list in groups:
            utils.debug(utils.shortest_common_supersequence(phrase_list))
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
    
    def get_time_phrase(self, hours, minutes):
        '''
        Placeholder method.
        '''
        return 'Load a module (or a project) to start working with Chasy.'
