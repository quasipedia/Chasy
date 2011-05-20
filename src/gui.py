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

        # MAIN WINDOW
        self.main_window = self.builder.get_object("main_window")
        self.modules_menu = self.builder.get_object("modules")
        self.output_text = self.builder.get_object("output_text") #time phrase

        # ABOUT DIALOGUE
        self.about_dialogue = self.builder.get_object("about_dialogue")

        # TEXT DUMP
        self.dump_window = self.builder.get_object("dump_window")
        self.dump_textview = self.builder.get_object("dump_textview")
        self.dump_buffer = self.builder.get_object("dump_buffer")

        # HEURISTICS
        self.heuristic_dialogue = \
                self.builder.get_object("heuristic_dialogue")
        self.heuristic_explanation_label = \
                self.builder.get_object("heuristic_explanation_label")
        self.msa_progress_bar = self.builder.get_object("heuristic_progress")
        self.msa_time_left_label = \
                self.builder.get_object("heuristic_time_left_label")
        self.msa_phase_label = \
                self.builder.get_object("heuristic_phase_label")

        # CLOCKFACE EDITOR
        self.cface_editor_window = \
                self.builder.get_object("cface_editor_window")
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

        # VIRTUAL WORDCLOCK
        self.vclock_window = self.builder.get_object("virtualclock_window")
        self.vclock_cface = self.builder.get_object("vclock_drawing")
        self.vclock_uppercase = self.builder.get_object("vwc_enoforce_upper")
        self.vclock_lowercase = self.builder.get_object("vwc_enoforce_lower")

        # INIT VALUES AND STATUS!
        self.hours = 0
        self.minutes = 0
        self.logic = logic.Logic(self.modules_menu, self.clock_change,
                                 self.update_clockface_stats)
        self.update_text()
        self.main_window.show_all()

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

    ##### MAIN WINDOW #####

    def on_main_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_hours_value_changed(self, widget, data=None):
        self.hours = int(widget.get_text())
        self.update_text()

    def on_minutes_value_changed(self, widget, data=None):
        self.minutes = int(widget.get_text())
        self.update_text()

    def update_text(self):
        phrase = self.logic.clock.get_time_phrase(self.hours, self.minutes)
        self.output_text.set_text(phrase)

    ##### MAIN MENU #####

    def clock_change(self):
        self.dump_window.hide()
        self.cface_editor_window.hide()
        self.vclock_window.hide()
        self.update_text()

    def on_about_activate(self, widget, data=None):
        self.about_dialogue.show()

    def on_file_save_activate(self, widget, data=None):
        self.logic.save_project()

    def on_file_open_activate(self, widget, data=None):
        self.logic.load_project()
        self.cface_editor_window.hide()
        self.vclock_window.hide()

    def on_dump_full_activate(self, widget, data=None):
        text = '\n'.join(self.logic.clock.get_phrases_dump(True))
        self.__write_in_dump(text)
        self.dump_window.show()

    def on_dump_textonly_activate(self, widget, data=None):
        text = '\n'.join(self.logic.clock.get_phrases_dump())
        self.__write_in_dump(text)
        self.dump_window.show()

    def on_analysis_word_stats_activate(self, widget, data=None):
        stats = self.logic.get_phrases_analysis()
        self.__write_in_dump(stats, 'courier')
        self.dump_window.show()

    def on_clockface_get_heuristics_activate(self, widget, data=None):
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

    def on_clockface_auto_distribution_activate(self, widget, data=None):
        tmp = self.on_clockface_get_heuristics_activate(None)
        if tmp == -1:
            return -1
        self.logic.show_clockface(self.clockface_image,
                                  self.col_number_adjustment,
                                  self.update_clockface_stats)
        self.cface_editor_window.show()

    ##### DUMP WINDOW #####

    def on_close_dump_button_clicked(self, widget, data=None):
        self.dump_window.hide()

    def on_dump_window_delete_event(self, widget, data):
        self.dump_window.hide()
        return True #prevent destruction

    ##### ABOUT DIALOG #####

    def on_about_dialogue_delete_event(self, widget, data=None):
        self.about_dialogue.hide()
        return True

    def on_about_dialogue_response(self, widget, data):
        self.about_dialogue.hide()

    ##### HEURISTICS WINDOW #####

    def on_stop_heuristic_button_clicked(self, widget, data=None):
        try:
            self.logic.halt_heuristic = True
            self.logic.supersequence.halt_heuristic = True
            self.logic.cface.halt_heuristic = True
        except AttributeError:
            pass  #some properties of logic aren't initialised immediately

    ##### CLOCKFACE EDITOR #####

    def on_cface_editor_window_delete_event(self, widget, data):
        self.cface_editor_window.hide()
        return True

    def on_col_number_spinbutton_value_changed(self, widget, data=None):
        # ClockFace.__init__ changes the value of the spinbutton, which in turn
        # trigger this method. But logic.cface is not yet set at this time,
        # hence the need for the exception handling.
        try:
            self.logic.cface.adjust_display_params(int(widget.get_text()))
            self.logic.cface.display()
        except AttributeError:
            pass

    def on_cface_editor_window_key_press_event(self, widget, data):
        kv = data.keyval
        # Stop signal propagation if handled
        if self.logic.manipulate_clockface(kv):
            return True

    def on_cfe_extra_sentence_clicked(self, widget, data=None):
        print('Insert extra sentence')

    def on_cfe_substr_optimisation_clicked(self, widget, data=None):
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

    def on_cfe_bin_packing_clicked(self, widget, data=None):
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

    def on_cfe_generate_virtual_clicked(self, widget, data=None):
        self.logic.generate_vclock(self.vclock_cface)
        self.vclock_window.show()
        self.logic.vclock.update()

    def update_clockface_stats(self, widget, data):
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

    ##### VIRTUAL WORDCLOCK #####

    def on_vclock_drawing_expose_event(self, widget, data=None):
        tmp = self.vclock_cface.allocation
        self.logic.vclock.refresh_params(max_pixel_dimension=min(tmp.width,
                                                                 tmp.height))
        self.logic.vclock.update()

    def on_virtualclock_window_delete_event(self, widget, data=None):
        self.vclock_window.hide()
        return True

    def on_vwc_font_button_font_set(self, widget, data=None):
        font_face = widget.get_font_name()
        self.logic.vclock.refresh_params(font_face=font_face)
        self.logic.vclock.update()

    def on_vwc_bkground_button_color_set(self, widget, data=None):
        self.logic.vclock.refresh_params(bkg_color=widget.get_color())
        self.logic.vclock.update()

    def on_vwc_unlit_button_color_set(self, widget, data=None):
        self.logic.vclock.refresh_params(unlit_color=widget.get_color())
        self.logic.vclock.update()

    def on_vwc_lit_button_color_set(self, widget, data=None):
        self.logic.vclock.refresh_params(lit_color=widget.get_color())
        self.logic.vclock.update()

    def on_vwc_customlit_button_color_set(self, widget, data=None):
        self.logic.vclock.refresh_params(custom_color=widget.get_color())
        self.logic.vclock.update()

    def on_vwc_charspace_spin_value_changed(self, widget, data=None):
        value = int(widget.get_text())/100.0
        self.logic.vclock.refresh_params(charspace=value)
        self.logic.vclock.update()

    def on_vwc_borderspace_spin_value_changed(self, widget, data=None):
        value = int(widget.get_text())/100.0
        self.logic.vclock.refresh_params(borderspace=value)
        self.logic.vclock.update()

    def vwc_enforce_case_toggled(self, widget, data=None):
        get_case = lambda x : 'lower' if 'lower' in \
                              gtk.Buildable.get_name(x) else 'upper'
        new_status = widget.get_active()
        other_widget = self.vclock_lowercase if \
                       widget == self.vclock_uppercase else \
                       self.vclock_uppercase
        if new_status == True:
            other_widget.set_active(False)
            value = get_case(widget)
            print(gtk.Buildable.get_name(widget))
        else:
            value = None
        self.logic.vclock.refresh_params(case=value)
        self.logic.vclock.update()

    def on_custom_phrase_combo_changed(self, widget, data=None):
        print('customphrase lit', data)
        self.logic.vclock.update()

    def on_save_cface_button_clicked(self, widget, data=None):
        print('save design', data)

    def on_save_screenshot_button_clicked(self, widget, data=None):
        self.logic.vclock.get_shot('svg')

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()