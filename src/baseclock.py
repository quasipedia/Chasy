# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import utils

class Clock(object):
    
    def get_time_phrase(self, hours, minutes):
        '''
        Placeholder method that should ALWAYS be overridden by clock modules.
        '''
        return 'ERROR: No module installed'
        
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
    
