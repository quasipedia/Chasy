#!/usr/bin/env python
# -*- coding: utf-8  -*-
'''
Convenience methods for managing the clock modules.
'''

import glob
import sys

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class ClockManager(object):

    '''
    Expose convenience methods for managing clock modules.

    Unless specified otherwise, modules are addressed using their
    human-readable name [defined within the module itself by __module_name__].
    '''

    def __init__(self):
        '''
        Imports all available clock modules and organise a human-readable
        list of them in the form {'human_name':imported_module_object}
        '''
        self.modules = {}
        for module_name in glob.glob("clocks/*.py"):
            module_name = module_name[7:-3]
            if module_name != '__init__':
                module_name = 'clocks.' + module_name
                __import__(module_name)
                imported = sys.modules[module_name]
                human_name = getattr(imported, 'Clock').__module_name__
                self.modules[human_name] = imported

    def _get_module_specialstring(self, module_name, property_name):
        '''
        Return the any of the special strings (__xxxx__) from a given module.
        '''
        tmp = getattr(self.modules[module_name], 'Clock')
        return getattr(tmp, '__'+property_name+'__')

    def get_all_languages(self):
        '''
        Return an ordered list of all the languages used in the modules.
        '''
        languages = []
        for module in self.modules.values():
            languages.append(getattr(module, 'Clock').__language__)
        return sorted(list(set(languages)))

    def get_all_module_names(self, language=None):
        '''
        Return an ordered list of all the loaded modules.
        If "language" is set, it only returns the modules whose clocks
        are in said language.
        '''
        if language == None:
            return [name for name in self.modules]
        tmp = lambda n : self._get_module_specialstring(n, 'language')
        return [name for name in self.modules if tmp(name) == language]

    def get_clock_instance(self, module_name):
        '''
        Return a clock instance from module "module_name"
        '''
        return self.modules[module_name].Clock()


    def get_module_description(self, module_name):
        '''
        Return the description of the module as given by its author.
        '''
        raw = self._get_module_specialstring(module_name, 'description')
        return ' '.join(raw.split())


def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()