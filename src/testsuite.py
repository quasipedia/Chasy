#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 15 Apr 2011

@author: mac
'''
import unittest
import utils
from utils import debug
from main import Logic

class LogicUtils(unittest.TestCase):
    
    '''
    Test logic utils
    '''
    
    def testWordSelect(self):
        '''Word selection via dictionary with multiple keys.'''
        test_list = {(1, 2, 'a', 'b'):'first',
                     (3, 4, 'c', 'two'):'second',
                     (5,):'third'}
        # Test retrieval by all keys 
        for keys in (test_list):
            for key in keys:
                word = utils.word_select(key, test_list)
                self.assertEqual(word, test_list[keys])
        # Test exception
        self.assertRaises(BaseException, utils.word_select, 'xxx', test_list)

    def testListsRightIndex(self):
        '''Finding last occurrence of an item in a list.'''
        test_list = [1, 2, 3, 'four', 4, 5, 'four', 'five', 'five', 
                     6, 4, 3, 2, 3, 'four', 2, 2, 2, 'eight', (1,2,3)]
        correct_answers = [(1, 0), (2, 17), (3, 13), (4, 10), (5, 5), (6, 9),
                           ('four', 14), ('five', 8), ('eight', 18), 
                           ((1,2,3), 19)]
        # Test correctness
        for value, index in correct_answers:
            self.assertEqual(index, utils.list_rindex(test_list, value))
        # Test exceptions
        self.assertRaises(ValueError, utils.list_rindex, test_list, 'xxx')


class Russian(unittest.TestCase):
    '''
    Test Russian phrases generation.
    '''
    logic = Logic('russian')
    
    def testRoundHour(self):
        '''Generation of "o'clock" sentences.'''
        known_values = {(0, 0):'Сейчас полночь', #or 'Сейчас ровно двенадцать часов ночи',
                        (1, 0):'Сейчас ровно один час ночи',
                        (2, 0):'Сейчас ровно два часа ночи',
                        (3, 0):'Сейчас ровно три часа ночи',
                        (4, 0):'Сейчас ровно четыре часа утра',
                        (5, 0):'Сейчас ровно пять часов утра',
                        (6, 0):'Сейчас ровно шесть часов утра',
                        (7, 0):'Сейчас ровно семь часов утра',
                        (8, 0):'Сейчас ровно восемь часов утра',
                        (9, 0):'Сейчас ровно девять часов утра',
                        (10, 0):'Сейчас ровно десять часов утра',
                        (11, 0):'Сейчас ровно одиннадцать часов утра',
                        (12, 0):'Сейчас полдень', #or 'Сейчас ровно двенадцать часов дня'
                        (13, 0):'Сейчас ровно один час дня',
                        (14, 0):'Сейчас ровно два часа дня',
                        (15, 0):'Сейчас ровно три часа дня',
                        (16, 0):'Сейчас ровно четыре часа дня',
                        (17, 0):'Сейчас ровно пять часов дня',
                        (18, 0):'Сейчас ровно шесть часов вечера',
                        (19, 0):'Сейчас ровно семь часов вечера',
                        (20, 0):'Сейчас ровно восемь часов вечера',
                        (21, 0):'Сейчас ровно девять часов вечера',
                        (22, 0):'Сейчас ровно десять часов вечера',
                        (23, 0):'Сейчас ровно одиннадцать часов вечера'}
        for k in known_values:
            self.assertEqual(self.logic.get_text(*k), known_values[k])
    
    def testToHour(self):
        '''Generation of russian sentences for <30 mins TO the round hour.'''
        known_values = {(1, 55):'Сейчас без пяти минут два ночи',
                        (9, 45):'Сейчас без четверти десять утра'}
        for k in known_values:
            self.assertEqual(self.logic.get_text(*k), known_values[k])
    
    def testPastHour(self):
        '''Generation of russian sentences for <30 mins FROM the round hour.'''
        known_values = {(8, 22):'Сейчас двадцать два минуты девятого утра',
                        (9, 30):'Сейчас половина десятого утра',
                        (9, 15):'Сейчас четверть десятого утра'}
        for k in known_values:
            self.assertEqual(self.logic.get_text(*k), known_values[k])
    
    
class Analysis(unittest.TestCase):
    '''
    Test analysis of phrases.
    '''
    logic = Logic()
    
    def testOrderRules(self):
        '''Generation of order rulesets.'''
        phrase_list = ['red green blue',
                       'red blue yellow',
                       'red blue yellow',
                       'red yellow red',
                       'yellow green red']
        order_rules = {'red':{'min_rep':2, 
                               'right_of':set(('yellow', 'green')), 
                               'left_of':set(('green', 'blue', 'yellow'))},
                        'green':{'min_rep':1, 
                                 'right_of':set(('red', 'yellow')), 
                                 'left_of':set(('blue','red'))},
                        'blue':{'min_rep':1, 
                                'right_of':set(('red', 'green')), 
                                'left_of':set(('yellow',))},
                        'yellow':{'min_rep':1, 
                                  'right_of':set(('red', 'blue')), 
                                  'left_of':set(('red', 'green'))}}
        tested_value = self.logic.get_order_rules(phrase_list)
        self.assertEqual(tested_value, order_rules)
        
    def testOrderBasic(self):
        '''Basic ordering test verified against known unique solution'''
        phrase_list = ['aaa bbb ccc',
                       'ddd eee fff',
                       'ccc ddd']
        order = ['aaa', 'bbb', 'ccc', 'ddd', 'eee', 'fff']
        rules = self.logic.get_order_rules(phrase_list)
        tested_value = self.logic.get_order(rules)
        self.assertEqual(tested_value, order)

    def testOrderTricky(self):
        '''Stress test for the ordering algorithm:
        - compare identical duplicate words (ccc)
        - create a duplicate word which is not explicitly used twice in the
          same sentence (eee)
        - sort alternate sequences (fff ggg fff ggg)
        '''
        phrase_list = ['eee aaa bbb ccc', 'ccc ddd eee', 'ccc ccc',
                       'eee fff ggg', 'ggg fff', 'ggg fff ggg']
        possible_orders = [['eee', 'aaa', 'bbb', 'ccc', 'ccc', 'ddd',
                            'eee', 'fff', 'ggg', 'fff', 'ggg',],
                           ['eee', 'aaa', 'bbb', 'ccc', 'ccc', 'ddd', 
                            'eee', 'ggg', 'fff', 'ggg', 'fff']]
        rules = self.logic.get_order_rules(phrase_list)
        order = self.logic.get_order(rules)
        self.assertTrue(order in possible_orders)
        
    def testOrderAdvanced(self):
        '''Advanced ordering test verified against known ruleset.'''
        phrase_sets = [['eee aaa bbb ccc',
                        'ccc ddd eee',
                        'ccc ccc ccc'],
                       ['aaa bbb ccc ddd eee',
                       'zzz ccc ddd',
                       'bbb eee fff zzz',
                       'aaa zzz xxx',
                       'ccc ddd xxx']]
        for set in phrase_sets:
            #Test for success
            rules = self.logic.get_order_rules(set)
            order = self.logic.get_order(rules)
            self.assertTrue(self.logic.test_order_on_rules(order, rules))
            #Test for failure
            order = ['eee', 'aaa', 'ccc', 'bbb', 'ccc', 'ddd', 'eee']
            self.assertFalse(self.logic.test_order_on_rules(order, rules))
                                
    def testOrderUltimate(self):
        '''Ultimate ordering test verified against initial phrases.'''
        phrase_list = ['aaa bbb ccc ddd eee',
                       'zzz ccc ddd',
                       'bbb eee fff zzz',
                       'aaa zzz xxx',
                       'ccc ddd xxx']
        ruleset = self.logic.get_order_rules(phrase_list)
        order = self.logic.get_order(ruleset)
        self.assertTrue(self.logic.test_order_on_phrases(order, phrase_list))
        
if __name__ == "__main__":
    unittest.main()
