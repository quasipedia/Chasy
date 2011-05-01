#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 14 Apr 2011

@author: mac
'''

import gtk
import logic

class Gui(object):

    '''
    Provide the visual environment for interacting with the boat from the PC.
    '''

    def __init__(self):
        self.gui_file = "../data/gui.xml"
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gui_file)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window")
        self.dump_window = self.builder.get_object("dump_window")
        self.dump_buffer = self.builder.get_object("dump_buffer")
        self.about_dialogue = self.builder.get_object("about_dialogue")
        self.modules_menu = self.builder.get_object("modules")
        self.output_text = self.builder.get_object("output_text")

        self.hours = 0
        self.minutes = 0

        self.logic = logic.Logic(self.modules_menu, self.update_text)
        self.update_text()
        
        self.window.show_all()
        
    ###### INPUT FOR TESTING TIMES #####
        
    def on_hours_value_changed(self, widget):
        self.hours = int(widget.get_text())
        self.update_text()
        
    def on_minutes_value_changed(self, widget):
        self.minutes = int(widget.get_text())
        self.update_text()
        
    ##### MENU COMMANDS ######    
    
    def on_dump_full_activate(self, widget):
        self.dump_buffer.set_text(
                        '\n'.join(self.logic.clock.get_phrases_dump(True)))
        self.dump_window.show()

    def on_dump_textonly_activate(self, widget):
        self.dump_buffer.set_text(
                            '\n'.join(self.logic.clock.get_phrases_dump()))
        self.dump_window.show()

    def on_analysis_word_stats_activate(self, widget):
        self.logic.get_phrases_analysis()
    
    ##### WINDOWS MANAGEMENT #####
        
    def on_close_dump_button_clicked(self, widget):
        self.dump_window.hide()

    def on_dump_window_delete_event(self, widget, data):
        self.dump_window.hide()
        return True #prevent destruction

    def on_about_activate(self, widget):
        self.about_dialogue.show()

    def on_about_dialogue_delete_event(self, widget):
        self.about_dialogue.hide()
        return True

    def on_about_dialogue_response(self, widget, data):
        self.about_dialogue.hide()

    def on_window_destroy(self, widget):
        gtk.main_quit()
        
    def update_text(self):
        phrase = self.logic.clock.get_time_phrase(self.hours, self.minutes)
        self.output_text.set_text(phrase)

if __name__ == '__main__':
    import clocks.fiveminutesenglish
    c = clocks.fiveminutesenglish.Clock()
    l = logic.Logic(None, None, True)  #debug configuration
    l.clock = c
    print(l.get_sequence())
    exit()
    Gui()
    gtk.main()