#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Ancestor for clock plugins.

All clock plugins should subclass from baseclock.Clock and should provide
at least the "__build_time_phrase" method.
'''

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Clock(object):

    def __init__(self, resolution, approx_method):
        self.resolution = resolution
        self.approx_method = approx_method

    def __build_time_phrase(self, hours, minutes):
        '''
        Placeholder method that should ALWAYS be overridden by clock modules.
        '''
        return 'ERROR: No module installed'

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

    def approximate(self, hours, minutes):
        '''
        Return a tuple (hours, minutes) of the input time according
        to the approximation method "method" applied with a given "resolution"
        in minutes.
        '''
        input = hours*60 + minutes
        res = self.resolution
        if self.approx_method == 'closest':
            output = int(round(input/float(res)) * res)
        if self.approx_method == 'last':
            output = input/res * res
        return (output/60, output%60)

    def get_time_phrase(self, hours, minutes):
        return self.__build_time_phrase(*self.approximate(hours, minutes))

    def get_phrases_dump(self, with_numbers=False):
        '''
        Generate the dump of all the time phrases in a day (1440 for a minute-
        accurate clock). If 'with_numbers' is True, prepend a numeric
        representation of the time in the form HH:MM.
        '''
        phrases = []
        # Generate phrases
        for h in range(24):
            for m in range(60):
                phrase = ''
                if with_numbers == True:
                    phrase += str(h).zfill(2) + ':' + str(m).zfill(2) + '  '
                phrases.append(phrase + self.get_time_phrase(h, m))
        # Check for uniqueness
        return phrases


def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()