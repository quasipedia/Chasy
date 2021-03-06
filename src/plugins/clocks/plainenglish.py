#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Clock plugin providing sentences in standard English.
'''

import models.baseclock

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Stable"


class Clock(models.baseclock.Clock):

    '''
    Plain English clock.
    '''

    __module_name__ = 'Standard English 12h'
    __language__ = 'English'
    __authors__ = 'Mac Ryan'
    __description__ = '''Plain twelve hours based English clock. Sentences
    repeat every 12 hours (there are no 'am' or 'pm').'''

    nums = {0:'twelve',
            1:'one',
            2:'two',
            3:'three',
            4:'four',
            5:'five',
            6:'six',
            7:'seven',
            8:'eight',
            9:'nine',
            10:'ten',
            11:'eleven',
            12:'twelve',
            13:'thirteen',
            14:'fourteen',
            15:'quarter',
            16:'sixteen',
            17:'seventeen',
            18:'eighteen',
            19:'nineteen',
            20:'twenty',
            21:'twenty-one',
            22:'twenty-two',
            23:'twenty-three',
            24:'twenty-four',
            25:'twenty-five',
            26:'twenty-six',
            27:'twenty-seven',
            28:'twenty-eight',
            29:'twenty-nine',
            30:'half'}

    def __build_time_phrase(self, hours, minutes):
        '''
        Return the sentence meaning "it's hours:minute".
        This method is the only method to make a module for Chasy.
        '''
        words = ["It", "is"]
        if 0 < minutes < 31:
            words.append(self.nums[minutes])
            words.append("past")
        elif minutes > 30:
            words.append(self.nums[60-minutes])
            words.append("to")
            hours += 1
        words.append(self.nums[hours%12])
        if minutes == 0:
            words.append("o'clock")
        return ' '.join(words)


def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()