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

class Utils(unittest.TestCase):
    
    '''
    Test the utils
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
        self.assertRaises(Exception, utils.word_select, 'xxx', test_list)

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

    def testConversion(self):
        '''Multiple tests for the conversion function:
        - Coding generates expected string.
        - Coding works on both strings and list of strings.
        '''        
        single_phrase = 'The brave guy jumped over the fence'
        multiple_phrases = ['The red herring swims',
                            'The red herring sinks',
                            'The blue cat swims']
        keys = {'blue':'!', 'the':'£', 'brave':'$', 'sinks':'%', 'fence':'^', 
                'jumped':'&', 'over':'*', 'swims':';', 'The':'@', 'cat':'#',
                'herring':'~', 'guy':'=', 'red':'-'}
        expected_phrase = '@ $ = & * £ ^'
        expected_phrases = ['@ - ~ ;', '@ - ~ %', '@ ! # ;']
        self.assertEqual(utils.convert(keys, single_phrase), expected_phrase)
        self.assertEqual(utils.convert(keys, multiple_phrases), 
                         expected_phrases)
        # Test for wrong stuff type
        self.assertRaises(Exception, utils.convert, keys, {'s':'No go'})
        
    def testPhraseGrouping(self):
        '''Grouping similar phrases together.'''
        phrases = ["it is five past one",
               "it is one to two",
               "it is two to three",
               "it is three to four",
               "it is four to five",
               "it is five to six",
               "it is four past seven",
               "it is three past eight",
               "it is two past nine",
               "it is one past ten",
               "it is eleven o'clock",
               "it is twelve o'clock",
               "it is one o'clock",
               "it is two o'clock",
               "it is three o'clock",
               ]
        expected_groups = [["it is one to two", "it is three to four", 
                            "it is four to five", "it is five to six", 
                            "it is two to three"]
                           ["it is two o'clock", "it is one o'clock", 
                            "it is eleven o'clock", "it is three o'clock", 
                            "it is twelve o'clock"]
                           ["it is one past ten", "it is five past one", 
                            "it is two past nine", "it is four past seven", 
                            "it is three past eight"]]
        self.assertEqual(utils.group_similar_phrases(phrases), expected_groups)

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
        known_values = {(8, 22):'Сейчас двадцать две минуты девятого утра',
                        (9, 30):'Сейчас половина десятого утра',
                        (9, 15):'Сейчас четверть десятого утра'}
        for k in known_values:
            self.assertEqual(self.logic.get_text(*k), known_values[k])
    
    
class Analysis(unittest.TestCase):
    '''
    Test analysis of phrases.
    '''
    logic = Logic()
            
    def testOrderBasic(self):
        '''Sequence generation against known solution'''
        phrases = ['aaa bbb ccc',
                   'ddd eee fff',
                   'ccc ddd']
        order = ['aaa', 'bbb', 'ccc', 'ddd', 'eee', 'fff']
        self.assertEqual(self.logic.get_words_sequence(phrases), order)

    def testOrderTricky(self):
        '''Stress test for the sequence generation algorithm:
        - compare identical duplicate words (ccc)
        - create a duplicate word which is not explicitly used twice in the
          same sentence (eee)
        - sort alternate sequences (fff ggg fff ggg)
        '''
        phrases = ['eee aaa bbb ccc', 'ccc ddd eee', 'ccc ccc',
                       'eee fff ggg', 'ggg fff', 'ggg fff ggg']
        seq = self.logic.get_words_sequence(phrases)
        self.assertTrue(self.logic.test_sequence_against_phrases(seq, phrases))
        
    def testOrderLong(self):
        '''Sequence generation with long list of long sentences.'''
        phrases = ['the red carpet is unrolled on the floor',
                   'a cat is walking on the carpet',
                   'a cat is walking on a red floor',
                   'the logic of sentence generation is a red herring',
                   'no floor is too red not to get a herring carpet',
                   'the cat of the castle made a sentence',
                   'the logic of the herring is red',
                   'a cat and a herring are on the floor',
                   'no cat is on the carpet',
                   'no logic can hold against ideology']
        seq = self.logic.get_words_sequence(phrases)
        self.assertTrue(self.logic.test_sequence_against_phrases(seq, phrases))
        
if __name__ == "__main__":
    unittest.main()
