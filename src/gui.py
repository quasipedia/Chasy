#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Chasy's Graphic User Interface and callbacks.
'''

import gtk
import pango
import logic

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
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
        self.heuristic_explanation_label = \
                self.builder.get_object("heuristic_explanation_label")
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
        self.col_number_adjustment = \
                self.builder.get_object("col_number_adjustment")
        self.cf_word_number_entry = \
                self.builder.get_object("cf_word_number_entry")
        self.cf_width_entry = self.builder.get_object("cf_width_entry")
        self.cf_height_entry = self.builder.get_object("cf_height_entry")
        self.cf_ratio_entry = self.builder.get_object("cf_ratio_entry")
        self.cf_wasted_entry = self.builder.get_object("cf_wasted_entry")
        self.cf_optimisation_entry = \
                self.builder.get_object("cf_optimisation_entry")

        self.hours = 0
        self.minutes = 0

        self.logic = logic.Logic(self.modules_menu, self.module_change)
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

    ###### WINDOWS MANAGEMENT #####

    def on_close_dump_button_clicked(self, widget):
        self.dump_window.hide()

    def on_dump_window_delete_event(self, widget, data):
        self.dump_window.hide()
        return True #prevent destruction

    def prova(self, widget):
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

    def module_change(self):
        self.dump_window.hide()
        self.clockface_window.hide()
        self.update_text()

    ###### INPUT FOR TESTING TIMES #####

    def on_hours_value_changed(self, widget):
        self.hours = int(widget.get_text())
        self.update_text()

    def on_minutes_value_changed(self, widget):
        self.minutes = int(widget.get_text())
        self.update_text()

    def update_text(self):
        phrase = self.logic.clock.get_time_phrase(self.hours, self.minutes)
        self.output_text.set_text(phrase)

    ###### MENU COMMANDS ######

    def on_file_save_activate(self, widget):
        self.logic.save_project()

    def on_file_open_activate(self, widget):
        self.logic.load_project()
        self.clockface_window.hide()

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
        self.heuristic_explanation_label.set_markup(
        "Chasy is using <i>heuristic</i> to find a sequence of words from " +
        "which it will be possible to compose all the sentences of the " +
        "clock. It will take about a minute.\n\n" +
        "Be advised that although the sequence will work, <b>there is no " +
        "guarantee it is the shortest possible one</b>. Knowing the grammar " +
        "of the language in use, is sometimes possible to manually improve " +
        "the automatic solution.")
        self.msa_progress_bar.set_fraction(0)
        self.heuristic_dialogue.show()
        tmp = self.logic.get_sequence(
                                callback=self.__update_msa_progress_values)
        self.heuristic_dialogue.hide()
        if tmp == -1:
            return -1
        if widget != None:  # if the function has been called programmatically
            text = self.logic.supersequence.get_sequence_as_string()
            lines = '\n'.join(text.split())
            self.dump_buffer.set_text(lines)
            self.dump_window.show()

    def on_clockface_auto_distribution_activate(self, widget):
        tmp = self.on_clockface_get_heuristics_activate(None)
        if tmp == -1:
            return -1
        self.logic.show_clockface(self.clockface_image,
                                  self.col_number_adjustment)
        self.clockface_window.show()

    ###### HEURISTICS #####

    def on_stop_heuristic_button_clicked(self, widget):
        try:
            self.logic.halt_heuristic = True
            self.logic.supersequence.halt_heuristic = True
            self.logic.cface.halt_heuristic = True
        except AttributeError:
            pass  #some properties of logic aren't initialised immediately
    ###### CLOCKFACE-RELATED EVENTS #####

    def on_clockface_window_key_press_event(self, widget, data):
        kv = data.keyval
        # Stop signal propagation if handled
        if self.logic.manipulate_clockface(kv):
            return True

    def on_cfb_extra_sentence_clicked(self, widget):
        print('Insert extra sentence')

    def on_cfb_generate_cface_clicked(self, widget):
        print('Generate clockface image')
#        self.logic.cface.scene.write_svg_file('clockface.svg')
        self.logic.cface.generate_file()

    def on_cfb_substr_optimisation_clicked(self, widget):
        self.heuristic_explanation_label.set_markup(
        "Chasy is using <i>heuristic</i> (again!) to check if some words " +
        "can be displayed using only parts of larger encompassing words. It " +
        "will not take too long... Hold in there!\n\n" +
        "Be advised that we are still using heuristics here, so <b>it " +
        "might be possible that some <i>merging</i> that would be " +
        "possible won't be performed</b>.")
        self.heuristic_dialogue.show()
        self.logic.supersequence.substring_merging_optimisation(
                                callback=self.__update_msa_progress_values)
        self.heuristic_dialogue.hide()
        self.logic.cface.display()

    def on_cfb_bin_packing_clicked(self, widget):
        self.heuristic_explanation_label.set_markup(
        "Yeah! You guessed! Chasy is using <i>heuristic</i> one more time " +
        "to try packing your clockface as chock-a-block as she can! It is " +
        "impossible to estimate the amount of time needed for this " +
        "but it typically takes no longer than 5 minutes at worse\n\n" +
        "The usual disclaimer about heuristics applies here too: <b>there " +
        "is no guarantee the resulting clockface is the best possible " +
        "one</b>, but further optimisation - if at all possible - is " +
        "usually trivial for humans.")
        self.heuristic_dialogue.show()
        self.logic.cface.bin_pack(heur_callback=\
                                  self.__update_msa_progress_values)
        self.heuristic_dialogue.hide()

    def on_col_number_spinbutton_value_changed(self, widget):
        # ClockFace.__init__ changes the value of the spinbutton, which in turn
        # trigger this method. But logic.cface is not yet set at this time,
        # hence the need for the exception handling.
        try:
            self.logic.cface.adjust_display_params(int(widget.get_text()))
            self.logic.cface.display()
        except AttributeError:
            pass

    def on_clockface_image_expose_event(self, widget, data):
        '''
        React to any change in the clockface image.
        '''
        stats = self.logic.cface.get_stats()
        self.cf_word_number_entry.set_text(stats['word_number'])
        self.cf_width_entry.set_text(stats['width'])
        self.cf_height_entry.set_text(stats['height'])
        self.cf_optimisation_entry.set_text(stats['optimisation'])
        self.cf_wasted_entry.set_text(stats['wasted'])
        self.cf_ratio_entry.set_text(stats['ratio'])

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()