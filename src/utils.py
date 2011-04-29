# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

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
        
def group_similar_phrases(phrases, atomic_words=True):
    '''
    Group together phrases that have a common "positional rule". Return list.
    e.g.: ["it is one to three", "it is two to to four", "it is nine to ten"]
    - atomic_words: whether comparison is between words or letters
    - keep_blocks: whether return value should be a plain list of groups,
    ===> Because of the grouping algorithm, any sentence in the same group
    can be transformed into any other applying exactly the same operations.
    '''
    # Unless we want to operate at a char level, we need to transform sentences
    # into lists of words to make them "atomic" (i.e. "non- divisible")
    if atomic_words:
        for i, phrase in enumerate(phrases):
            phrases[i] = tuple(phrase.split())
        analyst = difflib.SequenceMatcher(None)
    else:
        analyst = difflib.SequenceMatcher(lambda x: x == ' ') # space as junk
    # Make sure phrases are unique
    phrases = set(phrases)
    # First group pairs that have the same proximity ratio and the same 
    # matching pattern (blocks + actual strings)...
    groups = {}
    for a, b in itertools.combinations(phrases, 2):
        analyst.set_seqs(a, b)
        ratio = int(math.floor(analyst.ratio()*1000)) #round has approx. errors
        blocks = tuple(analyst.get_matching_blocks())[:-1]  #need hashable!
        common_words = blocks_to_words(a, blocks)
        key = (ratio, blocks, common_words)
        if key not in groups.keys():
            groups[key] = set()
        groups[key].add(a)
        groups[key].add(b)
    # Then eliminate multiple memberships of phrases to different families
    # by giving priorities to families with higher ratio and within those 
    # with the same ratio, to those with higher number of members)
    priority = [k for k in groups]
    priority.sort(key=lambda x: len(groups[x]), reverse=True) # sort by size
    priority.sort(key=lambda x: x[0], reverse=True)
    assigned_phrases = set()
    for key in priority:
        groups[key] = groups[key].difference(assigned_phrases)
        assigned_phrases = assigned_phrases.union(groups[key])
    # Beautify the output removing keys and empty sets.
    groups = [[' '.join(phrase) for phrase in group] 
              for k, group in groups.items() if len(group) != 0]
    return groups

def shortest_common_supersequence(phrases):
    '''
    Return the shortest common supersequence between phrases. Words are atomic.
    '''
    supersequence = []
    phrases = [phrase.split() for phrase in phrases]
    for phrase in phrases:
        pass
    return supersequence

def blocks_to_words(a, blocks):
    '''
    Takes matching blocks and returns their intended fragment of string.
    '''
    # Tuples are necessary to make the output hashable (and therefore usable 
    # as part of a dictionary key). 
    output = []
    for i, j, l in blocks:  #remove dummy block (difflib feature)
        output.append(a[i:i+l])
    return tuple(output)