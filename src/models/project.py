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
    # Project settings grouping
    PRJ_STTNGS_PHRASES = ('clock', 'resolution', 'approx_method')

    def __init__(self):
        self.__gobject_init__()
        self.__reset_project()
        self.unsaved_flag = False

    def __reset_project(self):
        '''
        Reset all those properties of the object that are project-specific.
        '''
        for property in self.SAVE_MASK:
            if property != 'SCHEMA_VERSION':  # don't overwrite class property!
                setattr(self, property, None)
        self.saved_state = self.__get_masked_dict()
        self.last_save_fname = None
        self.unsaved_flag = False

    def __get_masked_dict(self):
        '''
        Returns a dictionary with the properties indicated in "SAVE_MASK".
        '''
        dict_ = {}
        for pr in self.SAVE_MASK:
            dict_[pr] = getattr(self, pr)
        return dict_

    def broadcast_change(self, skip_flag_setting=False):
        '''
        Check current values of the properties in SAVE_MASK against their
        values on last broadcast_change call. If the state is changed, it emits
        the signal "project_updated" with a dictionary of the properties that
        have changed as a parameter.
            It also set the "unsaved_flag" to True, unless the parameter
        'skip_flag_setting' is set to True (useful for when project is first
        loaded).
            Return True if the state of the project has changed.
        '''
        has_changed = False
        new_state = self.__get_masked_dict()
        if self.saved_state != new_state:
            has_changed = True
            if not skip_flag_setting:
                self.unsaved_flag = True
            data = {}
            for pr in self.SAVE_MASK:
                if self.saved_state[pr] != new_state[pr]:
                    data[pr] = new_state[pr]
            self.saved_state = new_state
            self.emit("project_updated", data)
        return has_changed

    def is_populated(self):
        '''
        Return True if the project is populated.
        '''
        for pr in self.SAVE_MASK:
            if pr != 'SCHEMA_VERSION' and getattr(self, pr) != None:
                return True
        return False

    def is_unsaved(self):
        '''
        Return True if the project has unsaved changes.
        '''
        return self.unsaved_flag

    def get_project_name(self):
        '''
        Return a suitable project name for the project.
        (Typically used in the main window title
        '''
        if not self.is_populated():
            return None
        if self.last_save_fname == None:
            name = '<new project>'
        else:
            name = os.path.split(self.last_save_fname)[1]
        return name

    def save(self, fname=None):
        '''
        Save to disk the essential data on the project. If fname is not given,
        uses the name used on the last save operation.
        '''
        # If the file have not been given an extension, uses the default one
        if fname and '.' not in os.path.split(fname)[1]:
            fname += '.' + self.DEFAULT_EXTENSION
        # Automatic save (no file name selection)
        if fname == None:
            assert self.last_save_fname != None
            fname = self.last_save_fname
        prj = dict()
        for property in self.SAVE_MASK:
            prj[property] = getattr(self, property)
        try:
            file_ = open(fname, 'w')
        except:
            problem_description = '''It was <b>impossible to open the requested
                file</b>. Hint: are you sure the saved file has the right
                permissions for <i>Chasy</i> to open it?'''
            self.emit("disk_operation_problem", problem_description)
            return -1
        # Protocol 0 (default one *will* generate problems with cyclic
        # reference of sequence and elements.
        pickle.dump(prj, file_, pickle.HIGHEST_PROTOCOL)
        file_.close()
        self.last_save_fname = fname
        self.unsaved_flag = False
        # Need to call this to update main window title
        self.emit("project_updated", None)

    def load(self, fname, installed_modules):
        '''
        Load a project from disk and regenerate the environment to match it.
        'installed_modules' is a list of the installed clock modules on the
        system. Trying to load a project based on an uninstalled module will
        generate a non fatal error.
        '''
        self.__reset_project()
        try:
            file_ = open(fname, 'r')
        except:
            problem_description = '''It was <b>impossible to open the requested
                file</b>. Hint: are you sure the saved file has the right
                permissions for <i>Chasy</i> to open it?'''
            self.emit("disk_operation_problem", problem_description)
            return -1
        try:
            prj = pickle.load(file_)
        except:
            problem_description = '''Although it was possible to open the
                project file, it was <b>impossible to decode the data</b> in
                it. Hint: are you sure the saved file is a <i>Chasy</i>
                project?'''
            self.emit("disk_operation_problem", problem_description)
            return -1
        file_.close()
        # Schema version compatibility check (mostly for future!)
        if prj['SCHEMA_VERSION'] != self.SCHEMA_VERSION:
            problem_description = '''The project is saved with a <b>schema
                version</b> (%s) which is incompatible with the one of the
                version of <i>Chasy</i> in use on this system.''' % \
                prj['SCHEMA_VERSION']
            self.emit("disk_operation_problem", problem_description)
            return -1
        del prj['SCHEMA_VERSION']
        # Verify required module is installed
        required = prj['project_settings']['clock']
        if required not in installed_modules:
            problem_description = '''The saved project is based the <b>"%s"
                clock module</b>, which is not installed on the system in use.
                ''' % required
            self.emit("disk_operation_problem", problem_description)
            return -1
        for property in prj:
            setattr(self, property, prj[property])
        self.last_save_fname = fname
        self.unsaved_flag = False
        self.broadcast_change(skip_flag_setting=True)

    def close(self):
        '''
        Close the current project.
        Note that the parameter for the signal is "None" and is a special case
        that each handler must process correctly.
        '''
        self.__reset_project()
        self.emit("project_updated", None)


# These lines register specific signals into the GObject framework.
gobject.type_register(Project)
gobject.signal_new("project_updated", Project, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new("disk_operation_problem", Project, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))


def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()