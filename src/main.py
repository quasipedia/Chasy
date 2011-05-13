#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Chasy - Word clock development platform.

Chasy (Russian for "clock") is a program aimed to assist the construction of
word clocks (i.e. a clock displaying the time in form of sentences instead of 
numbers). 
'''

import gtk
import gui

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"

if __name__ == '__main__':
    gui.Gui()
    gtk.main()