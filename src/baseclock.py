#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Ancestor for clock plugins.

All clock plugins should subclass from baseclock.Clock and should provide
at least the "get_time_phrase" method.
'''

__author__ = "Mac Ryan"
__copyright__ = "Copyright ${year}, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Clock(object):

    def _word_select(self, key, choices):
        '''
        Help method to select a given word in a dictionary in which keys are
        tuples. Example usage:
            minute_words = {1:'minute', tuple(range(2, 60):'minutes'}
            self.__word_select(4, minute_words)
        '''
        for keys, value in choices.iteritems():
            if key in keys:
                return value
        raise Exception("Key out of range: " + str(key))    
    
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
    

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()