# -*- coding: utf-8 -*-
'''
Created on 29 Apr 2011

@author: mac
'''

import baseclock

class Clock(baseclock.Clock):
    
    '''
    English clock with five-minutes precision
    '''
    
    __module_name__ = 'English 5 minute resolution'
    __authors__ = 'Mac Ryan'
    
    def __init__(self):
        '''
        Constructor
        '''
        self.nums = {0:'twelve',
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

    def get_time_phrase(self, hours, minutes):
        '''
        Return the sentence meaning "it's hours:minute".
        This method is the only method to make a module for Chasy.
        '''
        approx = lambda x: int(round(x/5.0) * 5)
        minutes = approx(minutes)
        if minutes == 60:
            minutes = 0
            hours += 1
        words = ["It", "is"]
        if 0 < minutes < 31:
            words.append(self.nums[minutes])
            words.append("past")
        elif 60 > minutes > 30:
            words.append(self.nums[60-minutes])
            words.append("to")
            hours += 1
        words.append(self.nums[hours%12])
        if minutes == 0:
            words.append("o'clock")
        return ' '.join(words)