#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Chasy's Graphic User Interface and callbacks.
'''

import gtk
import pango
import logic
import clockface

__author__ = "Mac Ryan"
__copyright__ = "Copyright ${year}, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


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
        self.dump_textview = self.builder.get_object("dump_textview")
        self.dump_buffer = self.builder.get_object("dump_buffer")
        self.heuristic_dialogue = \
                self.builder.get_object("heuristic_dialogue")
        self.msa_progress_bar = self.builder.get_object("heuristic_progress")
        self.msa_time_left_label = \
                self.builder.get_object("heuristic_time_left_label")
        self.msa_phase_label = \
                self.builder.get_object("heuristic_phase_label")
        self.about_dialogue = self.builder.get_object("about_dialogue")
        self.modules_menu = self.builder.get_object("modules")
        self.output_text = self.builder.get_object("output_text")
        self.clockface_window = self.builder.get_object("clockface_window")
        self.clockface_image = self.builder.get_object("clockface_image")

        self.hours = 0
        self.minutes = 0

        self.logic = logic.Logic(self.modules_menu, self.update_text)
        self.update_text()
        
        self.window.show_all()
        
    ###### HELPER FUNCTIONS #####

    def __write_in_dump(self, what, how='ubuntu'):
        '''
        Update the text in the dump window, using the font "how".
        '''
        self.dump_textview.modify_font(pango.FontDescription(how))
        self.dump_buffer.set_text(what)
        
    def __update_msa_progress_values(self, phase=None, time=None, bar=None):
        '''
        Update the MSA (multiple sequence alignment progress info.
        '''
        if phase:
            self.msa_phase_label.set_text(phase)
        if time:
            self.msa_time_left_label.set_text(time)
        if bar:
            self.msa_progress_bar.set_fraction(bar)
        else:
            self.msa_progress_bar.pulse()
        while gtk.events_pending():
            gtk.main_iteration(False)
    
    ###### INPUT FOR TESTING TIMES #####
        
    def on_hours_value_changed(self, widget):
        self.hours = int(widget.get_text())
        self.update_text()
        
    def on_minutes_value_changed(self, widget):
        self.minutes = int(widget.get_text())
        self.update_text()
        
    ##### MENU COMMANDS ######    
    
    def on_dump_full_activate(self, widget):
        text = '\n'.join(self.logic.clock.get_phrases_dump(True))
        self.__write_in_dump(text)
        self.dump_window.show()

    def on_dump_textonly_activate(self, widget):
        text = '\n'.join(self.logic.clock.get_phrases_dump())
        self.__write_in_dump(text)
        self.dump_window.show()

    def on_analysis_word_stats_activate(self, widget):
        stats = self.logic.get_phrases_analysis()
        self.__write_in_dump(stats, 'courier')
        self.dump_window.show()
    
    def on_clockface_get_heuristics_activate(self, widget):
        self.msa_progress_bar.set_fraction(0)
        self.heuristic_dialogue.show()
        self.logic.get_sequence(callback=self.__update_msa_progress_values)
        self.heuristic_dialogue.hide()
        lines = '\n'.join(self.logic.shortest_supersequence.split())
        self.dump_buffer.set_text(lines)
        self.dump_window.show()
    
    def on_clockface_auto_distribution_activate(self, widget):
        seq = self.logic.get_sequence()
        len_seq = sum([len(x.decode('utf-8')) for x in seq.split()])
        size = self.logic.get_minimum_panel_size(len_seq)
        self.cface = clockface.ClockFace(size[0], size[1], 
                                         self.clockface_image)
        self.cface.arrange_sequence(seq)
        self.cface.display()
        self.clockface_window.show()
    
    def on_clockface_window_key_press_event(self, widget, data):
        kv = data.keyval
        if kv == 65361:  #left arrow
            self.cface.change_selection('left')
        elif kv == 65363:  #right arrow
            self.cface.change_selection('right')
        elif kv == 65362:
            self.cface.change_selection('up')
        elif kv == 65364:
            self.cface.change_selection('down')
        elif unichr(kv) in ('a', 'A'):
            self.cface.move_selected_word('left')
        elif unichr(kv) in ('d', 'D'):
            self.cface.move_selected_word('right')
        elif unichr(kv) in ('w', 'W'):
            self.cface.move_current_line('up')
        elif unichr(kv) in ('s', 'S'):
            self.cface.move_current_line('down')
        self.cface.display()
        return True

    def on_stop_heuristic_button_clicked(self, widget):
        self.logic.halt_heuristic = True
        
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
    
    def on_clockface_window_delete_event(self, widget, data):
        self.clockface_window.hide()
        return True

    def on_about_dialogue_response(self, widget, data):
        self.about_dialogue.hide()

    def on_window_destroy(self, widget):
        gtk.main_quit()
        
    def on_cfb_save_file_clicked(self, widget):
        self.cface.scene.write_svg_file('clockface.svg')
        
    def update_text(self):
        phrase = self.logic.clock.get_time_phrase(self.hours, self.minutes)
        self.output_text.set_text(phrase)
        
        
def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()