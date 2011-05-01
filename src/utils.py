# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

This is a collection of helper functions used mostly in the Logic module
of the project.

@author: mac
'''

def debug(*stuff):
    '''
    Print "stuff" if the debug variable is set to True.
    '''
    debug_mode = True
    if debug_mode:
        strings = map(unicode, stuff)
        print(('>>>>>>>>>> DEBUG <<<<<<<<<<\n' + '\n'.join(strings)))

