# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import utils
import baseclock

class Clock(baseclock.Clock):
    
    '''
    Russian verbose clock.
    '''
    
    __module_name__ = 'Verbose Russian'
    __authors__ = 'Mac Ryan, Olga Andronova'
    
    def __init__(self):
        self.word_it_is = 'Сейчас'
        self.word_to = 'без'
        self.word_o_clock = 'ровно'
        self.word_quarter_nominative = 'четверть'
        self.word_quarter_genitive = 'четверти'
        self.word_half = 'половина'
        self.word_noon = 'полдень'
        self.word_midnight = 'полночь'
        self.words_hour = {('to_one_hour',1):'час',   #
                           ('to_two/three/four_hour', 2,3,4):'часа',
                           (5,6,7,8,9,10,11,12,13,14,15,16,17,
                            18,19,20,21,22,23,0):'часов'}
        self.words_minutes = {(1,21):'минута',
                              ('gen_1',2,3,4,22,23,24):'минуты',
                              ('gen_not_1',5,6,7,8,9,10,11,12,13,14,15,16,17,
                               18,19,20,25,26,27,28,29):'минут'}
        self.words_day_parts = {(4, 5, 6, 7, 8, 9, 10, 11):'утра',
                                (12, 13, 14, 15, 16, 17):'дня',
                                (18, 19, 20, 21, 22, 23):'вечера',
                                (0, 1, 2, 3, 24):'ночи'} #24 because of +1 ops
        self.cardinals_for_hours = {0:'двенадцать', #This is 12 and not 0!!!
                                    1:'один',
                                    2:'два',
                                    3:'три',
                                    4:'четыре',
                                    5:'пять',
                                    6:'шесть',
                                    7:'семь',
                                    8:'восемь',
                                    9:'девять',
                                    10:'десять',
                                    11:'одиннадцать',
                                    12:'двенадцать'}
        self.cardinals_nominative = {1:'одна',
                                     2:'две',
                                     3:'три',
                                     4:'четыре',
                                     5:'пять',
                                     6:'шесть',
                                     7:'семь',
                                     8:'восемь',
                                     9:'девять',
                                     10:'десять',
                                     11:'одиннадцать',
                                     12:'двенадцать',
                                     13:'тринадцать',
                                     14:'четырнадцать',
                                     15:'пятнадцать',
                                     16:'шестнадцать',
                                     17:'семнадцать',
                                     18:'восемнадцать',
                                     19:'девятнадцать',
                                     20:'двадцать'}
        self.cardinals_genitive = {1:'одной',
                                   2:'двух',
                                   3:'трёх',
                                   4:'четырёх',
                                   5:'пяти',
                                   6:'шести',
                                   7:'семи',
                                   8:'восьми',
                                   9:'девяти',
                                   10:'десяти',
                                   11:'одиннадцати',
                                   12:'двенадцати',
                                   13:'тринадцати',
                                   14:'четырнадцати',
                                   15:'пятнадцати',
                                   16:'шестнадцати',
                                   17:'семнадцати',
                                   18:'восемнадцати',
                                   19:'девятнадцати',
                                   20:'двадцати'}
        self.ordinals_genitive = {1:'первого',
                                  2:'второго',
                                  3:'третьего',
                                  4:'четвёртого',
                                  5:'пятого',
                                  6:'шестого',
                                  7:'седьмого',
                                  8:'восьмого',
                                  9:'девятого',
                                  10:'десятого',
                                  11:'одиннадцатого',
                                  12:'двенадцатого'}

    def get_time_phrase(self, hours, minutes):
        '''
        Return the sentence meaning "it's hours:minute".
        This method is the only method to make a module for Chasy.
        '''
        output = [self.word_it_is]
                
        # O'CLOCK CASE
        if minutes == 0:
            if hours == 12:
                output.append(self.word_noon)
            elif hours == 0:
                output.append(self.word_midnight)
            else:
                output.append(self.word_o_clock)
                output.append(self.cardinals_for_hours[hours%12])
                output.append(self._word_select(hours%12, self.words_hour))
                output.append(self._word_select(hours, self.words_day_parts))
        
        # <30 MINUTES TO FULL HOUR
        elif minutes > 30:
            output.append(self.word_to)
            # ADD PROPER NUMBER - looks convoluted, but it is so because 
            # it has been written thinking to the actual physical clock 
            # and the need to recycle the word "one, two, three..." for 
            # "twenty-one", "twenty-two", "twenty-three", etc...
            minutes_to = 60-minutes
            if minutes_to == 15:
                output.append(self.word_quarter_genitive)
            else:
                if minutes_to >= 20:
                    output.append(self.cardinals_genitive[20])
                    if minutes_to > 20:
                        output.append(self.cardinals_genitive[minutes_to-20])
                else:
                    output.append(self.cardinals_genitive[minutes_to])
                # ADD WORD 'MINUTES'
                if minutes_to == 1 or minutes_to == 21:
                    output.append(self._word_select('gen_1', 
                                                    self.words_minutes))
                else:
                    output.append(self._word_select('gen_not_1', 
                                                    self.words_minutes))
            # ADD THE HOUR THAT WILL COME
            if hours%12+1 == 1:
                output.append(self._word_select('to_one_hour', 
                                                self.words_hour))
            else:
                output.append(self.cardinals_for_hours[hours%12+1])
            # ONLY FOR 2, 3, 4 PM and 3 AM ADD WORD "часа"
            if hours+1 in (14, 15, 16, 3):
                output.append(self._word_select('to_two/three/four_hour', 
                                                self.words_hour))
            # APPEND DAY PERIOD
            output.append(self._word_select(hours+1, self.words_day_parts))
        
        # MAX 30 MINUTES AFTER FULL HOUR
        elif minutes <= 30:
            if minutes == 15:
                output.append(self.word_quarter_nominative)
            elif minutes == 30:
                output.append(self.word_half)
            else:
                if minutes >= 20:
                    output.append(self.cardinals_nominative[20])
                    if minutes > 20:
                        output.append(self.cardinals_nominative[minutes-20])
                else:
                    output.append(self.cardinals_nominative[minutes])
                output.append(self._word_select(minutes, self.words_minutes))
            output.append(self.ordinals_genitive[hours%12+1])
            # ONLY BETWEEN 11:01 AND 11:29 USE "утра" INSTEAD OF "дня"
            if hours == 11 and minutes != 30:
                output.append(self._word_select(hours, self.words_day_parts))
            else:
                output.append(self._word_select(hours+1, self.words_day_parts))
        
        # EXCEPTION
        else:
            raise(Exception, ' '.join(('Unrecognised time --- ', 
                                       str(hours), ':', str(minutes))))
        return ' '.join(output)