# -*- coding: utf-8 -*-
'''
Created on 25 Apr 2011

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
        strings = map(str, stuff)
        print('DEBUG>>>>> ' + ' '.join(strings))

def word_select(key, choices):
    '''
    Help method to select a given word in a dictionary based on the hour
    (the dictionary keys are tuples of possible hours)
    '''
    for keys, value in choices.iteritems():
        if key in keys:
            return value
    raise BaseException("Key out of range: " + str(key))    

def list_rindex(haystack, needle):
    '''
    Implementation of str.rindex() for lists.
    (Find last occurrence of an item in a list).
    '''
    return len(haystack)-haystack[::-1].index(needle)-1

def get_minimum_panel_size(chars):
    '''
    Return the closest panel size to a perfect square needed to contain chars.
    (Does NOT consider the need for non-truncating words)
    '''
    root = int(math.sqrt(chars))
    if root**2 >= chars:
        return (root, root)
    elif (root+1)*root >= chars:
        return (root+1, root)
    else:
        return (root+1, root+1)
    