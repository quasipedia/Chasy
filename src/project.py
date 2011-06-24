#!/usr/bin/env python
# -*- coding: utf-8  -*-
'''
Provide a class for storing project information.

Besides providing properties for storing data, the class also provides
packing, unpacking and other helper methods to provide basic manipulation
of projects (e.g. saving/loading from drive).
'''

import pickle


__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Project(object):

    '''
    A project object stores all available information on a given project.
    Normally used as singleton.
    '''

    DEFAULT_EXTENSION = 'sav'
    # Just to keep the door open for possible future non backward-
    # compatible changes...
    SCHEMA_VERSION = '1.0'
    # All properties of the objects that need to be saved (and loaded)
    SAVE_MASK = ['SCHEMA_VERSION',
                 'project_settings',
                 'vclock_settings',
                 'electronics_settings',
                 'supersequence']

    def __init__(self):
        # Initialise properties.
        for property in self.SAVE_MASK:
            setattr(self, property, None)

    def save(self, fname):
        '''
        Save to disk the essential data on the project.
        '''
        project = dict()
        for property in self.SAVE_MASK:
            project[property] = getattr(self, property)
        file_ = open(fname, 'w')
        # Protocol 0 (default one *will* generate problems with cyclic
        # reference of sequence and elements.
        pickle.dump(project, file_, pickle.HIGHEST_PROTOCOL)
        file_.close()

    def load(self, fname):
        '''
        Load a project from disk and regenerate the environment to match it.
        '''
        file_ = open(fname, 'r')
        project = pickle.load(file_)
        file_.close()
        # Schema version compatibility check (mostly for future!)
        assert project['SCHEMA_VERSION'] == self.SCHEMA_VERSION
        del project['SCHEMA_VERSION']
        for property in project:
            setattr(self, property, project[property])
#        cm = self.clock_manager
#        self.clock = cm.get_clock_instance(project['clock_module'])
#        self.swap_clock_callback()
#        if project['supersequence'] != None:
#            self.supersequence = project['supersequence']



def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()