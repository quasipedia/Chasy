# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

This is a collection of helper functions used mostly in the Logic module
of the project.

@author: mac
'''

import math

def debug(*stuff):
    '''
    Print "stuff" if the debug variable is set to True.
    '''
    debug_mode = True
    if debug_mode:
        strings = map(unicode, stuff)
        print(('>>>>>>>>>> DEBUG <<<<<<<<<<\n' + '\n'.join(strings)))

def word_select(key, choices):
    '''
    Help method to select a given word in a dictionary based on the hour
    (the dictionary keys are tuples of possible hours)
    '''
    for keys, value in choices.iteritems():
        if key in keys:
            return value
    raise Exception("Key out of range: " + str(key))    

def list_rindex(haystack, needle):
    '''
    Implementation of str.rindex() for lists.
    (Find last occurrence of an item in a list).
    '''
    return len(haystack)-haystack[::-1].index(needle)-1

def get_min_avg_max(string_series, what, return_as_text=True):
    '''
    Return a tuple with the lengths of the shortest, longest, and average
    string in the series. Length can be measured in words or characters. If
    characters is selected, then spaces are ignored.
    '''
    if what not in ('chars', 'words'):
        raise Exception("You can count either words or chars")
    count_f = {'words':lambda x: len(x.split()),
               'chars':lambda x: len(''.join(x.split()).decode("utf-8"))}
    lengths = sorted([count_f[what](string) for string in string_series])
    triplet = (lengths[1], sum(lengths)*1.0/len(lengths), lengths[-1])
    if return_as_text == True:
        triplet = "(%d, %.1f, %d)" % triplet
    return triplet
        
def blocks_to_words(s, blocks):
    '''
    Takes matching blocks and returns their intended fragment of string.
    Accepts block sequences from difflib, but without the last dummy block.
    '''
    # Tuples are necessary to make the output hashable (and therefore usable 
    # as part of a dictionary key). 
    output = []
    for i, j, l in blocks:  #dummy last block must have been removed by now. 
        output.append(s[i:i+l])
    return tuple(output)

def get_alternatives(phrases, position):
    '''
    Return an ordered list of all the different unique words (sorted) that
    are present in "phrases" at position "position".
    '''
    return sorted(set([phrase[position] for phrase in phrases]))

def get_combination_number(pool_size, sample_size):
    '''
    Return the number of sample_size big combinations without repetition that
    can be formed from a pool of pool_size).
    '''
    f = lambda x: math.factorial(x)
    return f(pool_size)/(f(sample_size)*f(pool_size - sample_size))