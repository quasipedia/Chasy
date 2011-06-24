#!/usr/bin/env python
# -*- coding: utf-8  -*-
'''
Provide a class for storing project information.

Besides providing properties for storing data, the class also provides
packing, unpacking and other helper methods to provide basic manipulation
of projects (e.g. saving/loading from drive).
'''

import pickle
import os.path
import gobject


__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Project(gobject.GObject):

    '''
    A project object stores all available information on a given project.
    Normally used as singleton; it's a gobject.GObject child in order to be
    able to be able to generate signals (see the bottom of this module).
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
        self.__gobject_init__()
        self.__reset_project()

    def __reset_project(self):
        '''
        Reset all those properties of the object that are project-specific.
        '''
        for property in self.SAVE_MASK:
            setattr(self, property, None)
        self.saved_state = self.__get_masked_dict()
        self.last_save_fname = None

    def __get_masked_dict(self):
        '''
        Returns a dictionary with the properties indicated in "SAVE_MASK".
        '''
        dict_ = {}
        for pr in self.SAVE_MASK:
            dict_[pr] = getattr(self, pr)
        return dict_

    def __broadcast_change(self):
        '''
        This generator check against the last saved state of the SAVE_MASK
        properties and the one of the project when __broadcast is called.
        If the state is changed, it emits the signal "project_updated" with
        a dictionary of the properties that have changed.
        Return True if the state of the project has changed.
        '''
        while True:
            has_changed = False
            new_state = self.__get_masked_dict()
            if self.saved_state != new_state:
                has_changed = True
                data = {}
                for pr in self.SAVE_MASK:
                    if self.saved_state[pr] != new_state[pr]:
                        data[pr] = new_state[pr]
                self.saved_state = new_state
                self.emit("project_updated", data)
            return has_changed

    def save(self, fname=None):
        '''
        Save to disk the essential data on the project. If fname is not given,
        uses the name used on the last save operation.
        '''
        # If the file have not been given an extension, uses the default one
        if '.' not in os.path.split(fname)[1]:
            fname += '.' + self.DEFAULT_EXTENSION
        # Automatic save (no file name selection)
        if fname == None:
            assert self.last_save_fname != None
            fname = self.last_save_fname
        prj = dict()
        for property in self.SAVE_MASK:
            prj[property] = getattr(self, property)
        file_ = open(fname, 'w')
        # Protocol 0 (default one *will* generate problems with cyclic
        # reference of sequence and elements.
        pickle.dump(prj, file_, pickle.HIGHEST_PROTOCOL)
        file_.close()
        self.last_save_fname = fname

    def load(self, fname):
        '''
        Load a project from disk and regenerate the environment to match it.
        '''
        self.__reset_project()
        file_ = open(fname, 'r')
        prj = pickle.load(file_)
        file_.close()
        # Schema version compatibility check (mostly for future!)
        assert prj['SCHEMA_VERSION'] == self.SCHEMA_VERSION
        del prj['SCHEMA_VERSION']
        for property in prj:
            setattr(self, property, prj[property])
        self.__broadcast_change()


# These lines register specific signals into the GObject framework.
gobject.type_register(Project)
gobject.signal_new("project_updated", Project, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))


def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()