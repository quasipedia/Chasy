# -*- coding: utf-8 -*-
'''
Created on 25 Apr 2011

This is a collection of helper functions used mostly in the Logic module
of the project.

@author: mac
'''

import math
import difflib
import itertools

def debug(*stuff):
    '''
    Print "stuff" if the debug variable is set to True.
    '''
    debug_mode = True
    if debug_mode:
        strings = map(unicode, stuff)
        print(('DEBUG>>>>> ' + ' '.join(strings)))

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

def get_minimum_panel_size(chars):
    '''
    Return the closest panel size to a perfect square needed to contain chars.
    (Does NOT consider the need for non-truncating words)
    '''
    root = int(math.sqrt(chars))
    if root**2 >= chars:
        x, y = root
    elif (root+1)*root >= chars:
        x, y = root+1, root
    else:
        x, y = root+1, root+1
    extra_cells = x*y-chars
    return x, y, extra_cells

def convert(keys, stuff):
    '''
    Encode or decode "stuff" on the basis of "keys", which is a dictionary
    in the form {stuff_symbol : target_symbol}.
    "stuff" can be a string or an iterable of strings.
    '''
    # convert a single string
    convert_string = lambda k,s : ' '.join([k[w] for w in s.split()])
    if type(stuff) in (str, unicode):
        return convert_string(keys, stuff)
    elif type(stuff) in (list, tuple, set):
        return [convert_string(keys, s) for s in stuff]
    else:
        raise Exception('stuff must be either a string or a list of strings',
                        str(type(stuff)))
        
def group_similar_phrases(phrases):
    '''
    Group together phrases that have a common "positional rule". Return list.
    e.g.: ["it is one to three", "it is two to to four", "it is nine to ten"] 
    '''
    # First group pairs that have the same proximity ratio and the same 
    # matching pattern (blocks + actual strings)...
    analyst = difflib.SequenceMatcher(lambda x: x == ' ')
    groups = {}
    for a, b in itertools.combinations(phrases, 2):
        analyst.set_seqs(a, b)
        ratio = int(math.floor(analyst.ratio()*1000))
        blocks = tuple(analyst.get_matching_blocks()) #need hashable!
        substrings = blocks_to_substrings(a, blocks)
        key = (ratio, blocks, substrings)
        if key not in groups.keys():
            groups[key] = set()
        groups[key].add(a)
        groups[key].add(b)
    # Then eliminate multiple memberships of phrases to different families
    # by giving priorities to families with higher ratio (and within those
    # with the same ration, those with higher number of members)
    priority = [k for k in groups]
    priority.sort(key=lambda x: len(groups[x]), reverse=True) # sort by size
    priority.sort(key=lambda x: x[0], reverse=True)
    assigned_phrases = set()
    for key in priority:
        groups[key] = groups[key].difference(assigned_phrases)
        assigned_phrases = assigned_phrases.union(groups[key])
    # Beautify the output removing keys and empty sets.
    groups = sorted([group for k, group in groups.items() if len(group) != 0])
    return groups
    # Then, further verify 
#    all_groups = []
#    for k, pairs in scores.items():
#        gg = transitive_affiliation(pairs)
#        for g in gg:
#            all_groups.append((k[0], g))
#    return all_groups

def blocks_to_substrings(a, blocks):
    '''
    Takes matching blocks and returns their intended fragment of string.
    '''
    output = ''
    for i, j, l in blocks:
        output += a[i:i+l]
    return output

def transitive_affiliation(pairs):
    '''
    If a|b and b|c then a|c, so a|b|c.  
    '''
    groups = []
    for a, b in pairs:
        added = False
        for group in groups:
            if a in group or b in group:
                group.add(a)
                group.add(b)
                added = True
        if not added:
            groups.append(set((a,b)))
    return groups