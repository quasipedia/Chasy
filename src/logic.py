# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import glob
import sys
import textwrap
import gtk
import itertools
import difflib
import math
import time
import utils

class ExtendedSequenceMatcher(difflib.SequenceMatcher):

    '''
    This class adds a couple of test methods to the standard difflib one.
    '''
    
    def are_isomorphic(self):
        '''
        Check if the transformation between A and B is the same of the
        transformation between B and A and if such transformation only 
        includes replacements.
        - Return False in case of A and B not being isomorphic
        - Return a tuple (ratio, matching_seqs, opcodes) if A and B are 
          isomorphic. All couple of isomorphic sentences that generate the same 
          tuple are isomorphic between themselves.
        '''
        if len(self.a) != len(self.b):
            return False
        matching_seqs = []
        codes = self.get_opcodes()
        for code in codes:
            if code[0] not in ('replace', 'equal'):
                return False
            if code[1:3] != code[3:5]:
                return False
            if code[0] == 'equal':
                matching_seqs.append(self.a[code[1]:code[2]])
        return (self.ratio(), tuple(matching_seqs), tuple(codes))

class Logic(object):
    
    '''
    Contains all the logic needed for the program to run, except the language
    specific functionality, which is given by individual clock modules.
    '''
    
    def __init__(self, parent_menu, callback, debug=False):
        # The program hasn't run a supersequence heuristic just yet...
        self.shortest_supersequence = None
        # The debug mode of using the class is command-line only...
        if debug == True:
            return
        # This callback is used to signal the need for a screen refresh
        self.invoke_refresh = callback
        # Imports all available clock modules and organise a human-readable
        # list of them in the form {'human_name':imported_module_object}
        self.available_modules = {}
        for module_name in glob.glob("clocks/*.py"):
            module_name = module_name[7:-3]
            if module_name != '__init__':
                module_name = 'clocks.' + module_name
                __import__(module_name)
                imported = sys.modules[module_name]
                human_name = getattr(imported, 'Clock').__module_name__
                self.available_modules[human_name] = imported
        # Populate the parent menu with modules names
        mod_menu = gtk.Menu()
        group = None
        for name in sorted(self.available_modules):
            item = gtk.RadioMenuItem(group, label=name)
            mod_menu.append(item)
            if group == None:
                group = item
                initial_module = name
            item.connect("toggled", self.switch_clock, name)
        parent_menu.set_submenu(mod_menu)
        # Pick the first module of the list to start with
        self.clock = self.available_modules[initial_module].Clock()
        group.set_active(True)
    
    def __get_min_avg_max(self, string_series, what, return_as_text=True):
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
    
    def __get_alternatives(self, phrases, position):
        '''
        Return an ordered list of all the different unique words (sorted) that
        are present in "phrases" at position "position".
        '''
        return sorted(set([phrase[position] for phrase in phrases]))
    
    def __get_combination_number(self, pool_size, sample_size):
        '''
        Return the number of sample_size big combinations without repetition that
        can be formed from a pool of pool_size).
        '''
        f = lambda x: math.factorial(x)
        return f(pool_size)/(f(sample_size)*f(pool_size - sample_size))
    
    def __get_orphans(self, phrases, families):
        '''
        Return the list of phrases which are not present in the family tree.
        (phrases is list, and families is list of lists) 
        '''
        phrases = list(set(phrases))  #ensure no duplicates
        for family in families:
            for phrase in family:
                try:
                    phrases.remove(phrase)
                except ValueError:  #in case phrase is not there...
                    pass
        return phrases
 
    def __get_isomorphic_families(self, phrases):
        '''
        Group together isomorphic sequences. That means that sentence A can 
        be transformed in sentence B by applying the same opcodes needed to 
        transform B into A. Return a list of lists.
        '''
        # Make sure phrases are unique
        phrases = list(set(phrases))
        # We need to transform sentences into lists of words to make words 
        # "atomic" (i.e. to prevent the analysis to get to char-based level)
        for i, phrase in enumerate(phrases):
            phrases[i] = tuple(phrase.split())
        # Progress monitor variables
        total = self.__get_combination_number(len(phrases), 2)
        counter = 0
        start = time.time()
        # Group isomorphic sentences by analysing isomorphism of pairs, and
        # adding them to sets of sentences with the same isomorphic pattern
        families = {}
        analyser = ExtendedSequenceMatcher()
        for a, b in itertools.combinations(phrases, 2):
            counter += 1
            analyser.set_seqs(a, b)
            iso = analyser.are_isomorphic()
            # Only process isomorphic sentences
            if iso:
                # What below ensures no approx errors in ratios
                if iso not in families.keys():
                    families[iso] = set()
                families[iso].add(a)
                families[iso].add(b)
                # Update progress bar every 1000 steps
            if counter % 1000 == 0:
                progress_fraction = float(counter)/total
                now = time.time()
                time_left = (now-start)/progress_fraction*(1-progress_fraction)
                print('Progress: %.2f    Time left: %d minutes and %d seconds' 
                      % (progress_fraction*100, time_left/60, time_left%60))
        # Then eliminate multiple memberships of phrases to different families
        # by giving priorities to families with higher ratio and within those 
        # with the same ratio, to those with higher number of members)
        priority = [k for k in families]
        priority.sort(key=lambda x: len(families[x]), reverse=True) #fam. size
        priority.sort(key=lambda x: x[0], reverse=True) #affinity
        assigned_phrases = set()
        for key in priority:
            families[key] = families[key].difference(assigned_phrases)
            assigned_phrases = assigned_phrases.union(families[key])
        # Beautify the output removing keys and empty or single member sets.
        families = [tuple([' '.join(phrase) for phrase in family]) 
                  for k, family in families.items() if len(family) > 1]
        return families
    
    def __get_isomorphic_supersequence(self, phrases):
        '''
        Return the Shortest Common Supersequence between isomorphic phrases.
        Atomic words.
        '''
        # The key of this passage is to insert variable words in the common
        # root in an ordered way. Because of the nature of the program, it is 
        # highly possible that isomorphic phrases regard the substitutions of
        # numbers. Creating supersequences where inserted numbers follow the 
        # same pattern maximise the similitude between supersequences of
        # different families.
        phrases = [tuple(phrase.split()) for phrase in phrases]
        analyser = difflib.SequenceMatcher(None, phrases[0], phrases[1])
        mblocks = analyser.get_matching_blocks()[:-1]
        equal_positions = []
        for i, j, l in mblocks:
            for n in range(i, i+l):
                equal_positions.append(n)
        supersequence = []
        cursor = 0
        while cursor < len(phrases[0]):
            if cursor in equal_positions:
                supersequence.append(phrases[0][cursor])
            else:
                for alternative in self.__get_alternatives(phrases, cursor):
                    supersequence.append(alternative)
            cursor += 1
        return ' '.join(supersequence)

    def __merge_closest_match(self, phrases):
        '''
        Modify in place phrases, merging the two most similar phrases in it.
        '''
        # Make sure phrases are unique
        phrases = list(set(phrases))
        phrases = [phrase.split() for phrase in phrases]
        analyser = difflib.SequenceMatcher()
        # Find the closest pair
        closest = None
        for a, b in itertools.combinations(phrases, 2):
            analyser.set_seqs(a, b)
            ratio = analyser.ratio()
            if closest == None or ratio > closest[0]:
                closest = (ratio, a, b)
        # Merge the two: lengthy but safer, this works by adapting one
        # code at a time, and then re-performing the analysis until no
        # other codes but "equal" or "remove".
        # No isomorphic ==> A to B might be different than B to A
        for i, j in ((1, 2), (2, 1)):
            while True: 
                insertion = False
                # Recreating the object is necessary because of a documented
                # Python bug in libdiff that caches incorrectly opcodes.
                # (see http://bugs.python.org/issue9985)
                analyser = ExtendedSequenceMatcher(None,closest[i],closest[j])
                for code, aa, az, ba, bz in analyser.get_opcodes():
                    if code in ('insert', 'replace'):
                        fragment = closest[j][ba:bz]
                        for frag in reversed(fragment):
                            closest[i].insert(az, frag)
                        insertion = True
                        break
                if insertion == False:
                    break
        assert closest[1] == closest[2]
        # "Closest" lists have been modified in place (within phrases list)
        # so we keep one and eliminate the other. 
        phrases.remove(closest[2])
        return [' '.join(phrase) for phrase in phrases]

    def switch_clock(self, widget, clock_name):
        '''
        Swap between different clock modules.
        Refresh the screen and clear cached values as needed.
        '''
        if widget.get_active():
            self.clock = self.available_modules[clock_name].Clock()
            try:
                self.invoke_refresh()
            # If invoked during the __init__, the callback won't work!! So...
            except AttributeError:
                pass
            self.shortest_supersequence = None
    
    def get_phrases_analysis(self):
        '''
        Returns an analysis of the complete set of time sentences.
        '''
        stats = []
        phrase_list = self.clock.get_phrases_dump()
        phrase_set = set(phrase_list)
        word_set = set(' '.join(phrase_list).split())

        stats.append(("SENTENCES", ''))
        n_phrases = len(phrase_list)
        stats.append(("Number of sentences", n_phrases)) 
        n_unique_phrases = len(phrase_set)
        stats.append(("Number of unique sentences", n_unique_phrases))

        stats.append(("WORDS", ''))
        n_unique_words = len(word_set)
        stats.append(("Number of unique words", n_unique_words))
        words_per_sentence = self.__get_min_avg_max(phrase_set, 'words')
        stats.append(("Words per sentence (min, avg, max)", 
                      words_per_sentence))
        
        stats.append(("CHARS", ''))
        #len(unicode) would return bytesize of string, non number of chars
        n_chars = sum([len(w.decode("utf-8")) for w in word_set])
        stats.append(("Chars in unique words", n_chars))
        chars_per_word = self.__get_min_avg_max(word_set, 'chars')
        stats.append(("Chars per word (min, avg, max)", chars_per_word))
        chars_per_sentence = self.__get_min_avg_max(phrase_set, 'chars')
        stats.append(("Chars per sentence (min, avg, max)", 
                      chars_per_sentence))

        stats.append(("MATRIX SIZE", ''))        
        approx_board_size = self.get_minimum_panel_size(n_chars)
        stats.append(("Minimum board size (X, Y, extra cells)", 
                      approx_board_size))

        # Generate text data
        col_width = max(map(len, [t for t, v in stats])) + 7
        for t, v in stats:
            if v != '':
                t += ' '
                print(t.ljust(col_width, '.') + ' %s') % str(v)
            else:
                t = ' ' + t
                print(t.rjust(col_width, '>'))
        
        # Append disclaimer
        disclaimer = '''\
        Be aware that the board size indicated here is to
        be considered as an "hard bottom limit" below which is physically
        impossible to go. However it is possible that the actual matrix will 
        need to be larger to accommodate for logical and spatial needs.'''
        print('\n' + textwrap.fill(textwrap.dedent(disclaimer), col_width))

    def get_minimum_panel_size(self, chars):
        '''
        Return the closest panel size to a perfect square needed to contain 
        chars. (Does NOT consider the need for non-truncating words)
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
    
    def get_sequence(self, phrases=None, force_rerun=False):
        '''
        Return a common supersequence to all the phrases.
        The generation of the supersequence is done heuristically and there 
        is no guarantee the supersequence will be the shortest possible.
        If no phrases are passed as parameters, all the phrases for the
        currently active clock module will be used (so the supersequence 
        will be able to display the entire day on the clock). 
        '''
        # It's a long job! If already done, don't re-do it unless specifically
        # told so!
        if self.shortest_supersequence and force_rerun == False:
            return self.shortest_supersequence
        # No phrases means... all phrases!!!
        if phrases == None:
            phrases = self.clock.get_phrases_dump()
        # ISOMORPHIC LOOP
        # Group all sentences in "families" of isomorphic sentences and
        # find the shortest supersequence for each family. Repeat until
        # isomorphic families are no longer possible.
        while True:
            families = self.__get_isomorphic_families(phrases)
            if len(families) == 0:
                break
            orphans = self.__get_orphans(phrases, families)
            supseqs = []
            for family in families:
                supseqs.append(self.__get_isomorphic_supersequence(family))
            phrases = supseqs + orphans
        # GENERIC LOOP
        # Keep on merging the two most similar sentences in the pool until 
        # the pool size is down to 1 unit.
        while len(phrases) > 1:
            phrases = self.__merge_closest_match(phrases)
        return phrases[0]

    def test_sequence_against_phrases(self, sequence, phrases):
        '''
        Test if a given sequence of words can be used to generate all the 
        time phrases. Return True for passed.
        '''
        for phrase in phrases:
            cursor = 0
            for word in phrase:
                try:
                    cursor += sequence[cursor:].index(word) 
                except ValueError:
                    return False
        return True
