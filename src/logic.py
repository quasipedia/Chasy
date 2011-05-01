# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import glob
import sys
import utils
import textwrap
import gtk
import itertools
import difflib
import math
import time

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
 
    def __get_families(self, phrases, atomic_words=True):
        '''
        Group together phrases that have a common "positional rule". Return 
        list. Exemple: ["it is one to three", "it is two to to four", 
        "it is nine to ten"]
        - atomic_words: whether comparison is between words or letters
        - keep_blocks: whether return value should be a plain list of groups,
        '''
        # Unless we want to operate at a char level, we need to transform 
        # sentences into lists of words to make them "atomic" (i.e. 
        # "non-divisible")
        if atomic_words:
            for i, phrase in enumerate(phrases):
                phrases[i] = tuple(phrase.split())
            analyser = difflib.SequenceMatcher(None)
        else:
            analyser = difflib.SequenceMatcher(lambda x: x == ' ') # ' ' = junk
        # Make sure phrases are unique
        phrases = set(phrases)
        # Progress monitor variables
        total = utils.get_combination_number(len(phrases), 2)
        current = 0
        start = time.time()
        # First group pairs that have the same proximity ratio and the same 
        # matching pattern (blocks + actual strings)...
        groups = {}
        for a, b in itertools.combinations(phrases, 2):
            current += 1
            # No same length = No same family
            if len(a) != len(b):
                # Nonsense key values to make it unique
                groups[(0, (a, b), 'skip')] = set((a, b)) 
                continue
            analyser.set_seqs(a, b)
            # The rounding function with decimals makes approximation errors
            # related to the floating point internal representation of nums
            ratio = int(math.floor(analyser.ratio()*1000))
            blocks = tuple(analyser.get_matching_blocks())[:-1]  #need hashable!
            common_words = utils.blocks_to_words(a, blocks)
            key = (ratio, blocks, common_words)
            if key not in groups.keys():
                groups[key] = set()
            groups[key].add(a)
            groups[key].add(b)
            if current % 1000 == 0:
                progress_fraction = float(current)/total
                now = time.time()
                time_left = (now-start)/progress_fraction*(1-progress_fraction)
                print('Progress: %.2f    Time left: %d minutes and %d seconds' 
                      % (progress_fraction*100, time_left/60, time_left%60))
        # Then eliminate multiple memberships of phrases to different families
        # by giving priorities to families with higher ratio and within those 
        # with the same ratio, to those with higher number of members)
        priority = [k for k in groups]
        priority.sort(key=lambda x: len(groups[x]), reverse=True) #size
        priority.sort(key=lambda x: x[0], reverse=True) #affinity
        assigned_phrases = set()
        for key in priority:
            groups[key] = groups[key].difference(assigned_phrases)
            assigned_phrases = assigned_phrases.union(groups[key])
        # Beautify the output removing keys and empty sets.
        groups = [[phrase for phrase in group] 
                  for k, group in groups.items() if len(group) != 0]
        return groups
    
    def __get_family_supersequence(self, phrases):
        '''
        Return the Shortest Common Supersequence between phrases. Atomic words.
        Works only for families in which all phrases have the same length.
        '''
        # The key of this passage and to perform substitutions in an ordered
        # way. Because of the nature of the program, it is highly possible that
        # substitutions in phrases regard numbers. Creating supersequences
        # where inserted numbers follow the same pattern maximise the 
        # similitude between supersequences of different families.
        #
        # Because of the family creation algorithm, we know that any
        # transformation between two phrases of the same family follow
        # exactly the same pattern. Furthermore we know that the matching
        # blocks on each phrase are in the SAME place.
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
                for alternative in utils.get_alternatives(phrases, cursor):
                    supersequence.append(alternative)
            cursor += 1
        print('SUPER', supersequence)
        return ' '.join(supersequence)

    def __get_general_supersequence(self, phrases):
        '''
        Return a supersequence for a sentences that do not necessarily
        resemble too much.
        '''
        phrases = [phrase.split() for phrase in phrases]
        analyser = difflib.SequenceMatcher()
        print("ENTER", phrases)
        while len(phrases) > 1:
            # Find the closest pair
            closest = None
            for a, b in itertools.combinations(phrases, 2):
                analyser.set_seqs(a, b)
                ratio = analyser.ratio()
                if closest == None or ratio > closest[0]:
                    closest = (ratio, a, b)
            # Remove it from the pool
            phrases.remove(closest[1])
            phrases.remove(closest[2])
            # merge the two: lengthy but safer, this works by adapting one
            # code at a time, and then re-performing the analysis until no
            # other codes but "equal" or "remove".
            while True:
                insertion = False
                analyser.set_seqs(closest[1], closest[2])
                for code, aa, az, ba, bz in analyser.get_opcodes():
                    if code in ('insert', 'replace'):
                        closest[1].insert(az, closest[2][ba:bz])
                        insertion = True
                        break  #not replacing but inserting screws up indexes!
                if insertion == False:
                    phrases.append(closest[1])
        print('EXIT', phrases)
        return phrases[0]

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
        words_per_sentence = utils.get_min_avg_max(phrase_set, 'words')
        stats.append(("Words per sentence (min, avg, max)", 
                      words_per_sentence))
        
        stats.append(("CHARS", ''))
        #len(unicode) would return bytesize of string, non number of chars
        n_chars = sum([len(w.decode("utf-8")) for w in word_set])
        stats.append(("Chars in unique words", n_chars))
        chars_per_word = utils.get_min_avg_max(word_set, 'chars')
        stats.append(("Chars per word (min, avg, max)", chars_per_word))
        chars_per_sentence = utils.get_min_avg_max(phrase_set, 'chars')
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
        # It's a long job! If already down, don't re-do it unless specifically
        # told so!
        if self.shortest_supersequence and force_rerun == False:
            return self.shortest_supersequence
        # No phrases means... all phrases!!!
        if phrases == None:
            phrases = self.clock.get_phrases_dump()
        # Group all sentences in "families" of similar sentences and
        # find the shortest supersequence for each family. Repeat until
        # families are no longer possible
        while True:
            families = self.__get_families(phrases)
            print('FAMILIES:', families)
            phrases = []
            for family in families:
                no_more_families = True
                if len(family) > 1 and utils.check_all_same_lenght(family):
                    phrases.append(self.__get_family_supersequence(family))
                    no_more_families = False
                else:
                    phrases.append(' '.join(family[0]))
            if no_more_families:
                break
        # Do the last merging between sequences that aren't anymore relatives
        print('END OF FAMILIES', phrases)
        return self.__get_general_supersequence(phrases)

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
