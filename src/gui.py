#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Chasy's Graphic User Interface and callbacks.
'''

import gtk
import gobject
import pango
import logic

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Gui(gobject.GObject):

    '''
    Provide the visual environment for interacting with the boat from the PC.
    '''

    def __init__(self):
        self.logic = logic.Logic()
        # Connect after, because the Gui() needs Logic() handlers to
        # process the project data first
        self.logic.project.connect_after("project_updated",
                                         self.on_project_updated)

        self.gui_file = "../data/gui.xml"
        self.builder = gtk.Builder()
        go = self.builder.get_object
        self.builder.add_from_file(self.gui_file)
        self.builder.connect_signals(self)

        # MAIN WINDOW
        self.main_window = go("main_window")
        self.modules_menu = go("modules")
        self.output_text = go("output_text") #time phrase
        self.sync_checkbox = go("keep_in_sync")
        self.hours_box = go("hours")
        self.minutes_box = go("minutes")
        self.menubar = go("menu_bar")
        # Menu items that can be sensitive even without a project
        self.safe_menuitems = ['file_new', 'file_open', 'file_quit',
                               'help_about']

        # PROJECT SETTINGS WINDOW
        self.settings_window = go("settings_window")

        # ABOUT DIALOGUE
        self.about_dialogue = go("about_dialogue")

        # TEXT DUMP
        self.dump_window = go("dump_window")
        self.dump_textview = go("dump_textview")
        self.dump_buffer = go("dump_buffer")

        # HEURISTICS
        self.heuristic_dialogue = go("heuristic_dialogue")
        self.heuristic_explanation_label = go("heuristic_explanation_label")
        self.msa_progress_bar = go("heuristic_progress")
        self.msa_time_left_label = go("heuristic_time_left_label")
        self.msa_phase_label = go("heuristic_phase_label")

        # CLOCKFACE EDITOR
        self.cface_editor_window = go("cface_editor_window")
        self.clockface_image = go("clockface_image")
        self.col_number_adjustment = go("col_number_adjustment")
        self.cf_word_number_entry = go("cf_word_number_entry")
        self.cf_width_entry = go("cf_width_entry")
        self.cf_height_entry = go("cf_height_entry")
        self.cf_ratio_entry = go("cf_ratio_entry")
        self.cf_wasted_entry = go("cf_wasted_entry")
        self.cf_optimisation_entry = go("cf_optimisation_entry")

        # VIRTUAL WORDCLOCK
        self.vclock_cface = go("vclock_drawing")
        self.vclock_settings = go("vclock_settings")
        self.vclock_uppercase = go("vwc_enoforce_upper")
        self.vclock_lowercase = go("vwc_enoforce_lower")

        # PROJECT SETTING WINDOW
        self.sttng_modlang_combo = go("sttng_module_lang_combo")
        self.sttng_modname_combo = go("sttng_module_name_combo")
        self.sttng_accuracy_combo = go("sttng_accuracy_combo")
        self.sttng_approx_closest = go("approx_closest")
        self.sttng_approx_last = go("approx_last_step")
        self.sttng_mod_description = go("sttng_mod_description")
        self.sttng_mod_textbuffer = go("module_description_buffer")
        self.__populate_settings()

        # FILE CHOOSER
        self.file_chooser_window = go("file_chooser")
        self.file_open_button = go("open_file_button")
        self.file_save_button = go("save_file_button")

        # INIT VALUES AND STATUS!
        self.hours = 0
        self.minutes = 0
        self.keep_sync = False
        self.__set_safe_mode(True)

        self.main_window.show()


    ###### HELPER METHODS #####

    def __populate_combo(self, combo, entries, select=None):
        '''
        Populate a combo with a series of values.
        Optionally select the "select" entry as default.
        '''
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        for i in entries:
            liststore.append([unicode(i)])
        combo.set_model(liststore)
        cell = gtk.CellRendererText()
        combo.clear()  #Needed if the combo was already populated
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        if select != None:
            assert select < len(entries)
            combo.set_active(select)

    def __populate_clock_modules_combo(self):
        '''
        Populate the clock modules combo box.
        This is a separate method as this population is done according to a
        filter that can change, so it needs to be performed not only at
        initialisation time.
        '''
        index = self.sttng_modlang_combo.get_active()
        # first entry is in language box is '---' which is "no filter"
        lang = None if index == 0 else self.clock_languages_entries[index]
        cm = self.logic.clock_manager
        self.clock_modules_entries = cm.get_all_module_names(lang)
        self.__populate_combo(self.sttng_modname_combo,
                              self.clock_modules_entries, 0)

    def __populate_settings(self):
        '''
        Populate all the options in the setting window.
        '''
        # Clock accuracy
        self.resolution_entries = [1, 2, 3, 5, 10, 15, 20, 30 ,60]
        self.__populate_combo(self.sttng_accuracy_combo,
                              self.resolution_entries, 0)
        # Clock languages
        cm = self.logic.clock_manager
        self.clock_languages_entries = cm.get_all_languages()
        self.clock_languages_entries.insert(0, '*all*')
        self.__populate_combo(self.sttng_modlang_combo,
                              self.clock_languages_entries, 0)
        # Clock modules
        self.__populate_clock_modules_combo()

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

    def __sync_with_system_clock(self):
        '''
        Update currently displayed time with system clock.
        '''
        if self.keep_sync == False:
            return False  #Remove this callback from the gtk main loop
        current_time = self.logic.get_current_time()
        if (self.hours, self.minutes) != current_time:
            self.hours, self.minutes = current_time
            self.hours_box.set_text(str(self.hours))
            self.minutes_box.set_text(str(self.minutes))
            self.update_text()
            return True  #Keep the the callback in the main loop

    def __show_vclock_elements(self, show):
        '''
        Show or hide GUI elements that have to do with the virtual clock.
        '''
        assert show in (True, False)
        if show:
            self.vclock_cface.show()
            self.vclock_settings.show()
        else:
            self.vclock_cface.hide()
            self.vclock_settings.hide()


    def __set_safe_mode(self, safestate):
        '''
        The 'safe mode' is the mode in which the program runs without an
        open project (for example at startup or if a project has been closed).
        This helper method deactivate all menu entries and other UI elements
        that are project-related. It only modifies elements in the main window.
        safestate == True → safe mode ON
        safestate == False → safe mode OFF.
        '''
        assert safestate in (True, False)
        # Toggling conditions
        self.sync_checkbox.set_sensitive(not safestate)
        self.hours_box.set_sensitive(not safestate)
        self.minutes_box.set_sensitive(not safestate)
        for elem in self.menubar.get_children():
            for item in elem.get_submenu().get_children():
                item.set_sensitive(not safestate)
        # State-specific conditions
        if safestate:
            for menuitem_name in self.safe_menuitems:
                menuitem = self.builder.get_object(menuitem_name)
                menuitem.set_sensitive(True)
            self.__show_vclock_elements(False)
            self.update_text(reset=True)
        elif self.logic.project.supersequence != None:
            self.__show_vclock_elements(True)

    def _supersequence_heuristics_show_dialogue(self):
        '''
        Display the heuristics dialogue when computing the supersequence.
        '''
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
        self.logic.get_sequence(callback=self.__update_msa_progress_values)
        self.heuristic_dialogue.hide()

    ##### SPECIAL HANDLERS #####
    # Special handlers are generic handlers or non GUI-generated handlers

    def on_project_updated(self, widget, data=None):
        '''
        This handles a signal from project, not from the GUI directly.
        '''
        # Safe mode?
        self.__set_safe_mode((True, False)[widget.is_populated()])
        # Make sense to display clockface editor and virtual clock?
        if widget.supersequence == None:
            self.__show_vclock_elements(False)
        self.dump_window.hide()
        self.update_text()

    def on_close_no_destroy(self, widget, data=None):
        '''
        This handles closing any window but the the main program one.
        It hides the window but prevent it's distrution by returning "True".
        The message can be generated by any widget within the window (for
        example a button).
        '''
        if not isinstance(widget, gtk.Window):
            widget = widget.get_parent_window()
        widget.hide()
        return True

    ##### MAIN WINDOW #####

    def on_main_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_keep_in_sync_toggled(self, widget, data=None):
        self.keep_sync = widget.get_active()
        if self.keep_sync:
            gobject.timeout_add(500, self.__sync_with_system_clock)
            self.hours_box.set_sensitive(False)
            self.minutes_box.set_sensitive(False)
        else:
            self.hours_box.set_sensitive(True)
            self.minutes_box.set_sensitive(True)

    def on_hours_value_changed(self, widget, data=None):
        self.hours = int(widget.get_text())
        self.update_text()

    def on_minutes_value_changed(self, widget, data=None):
        self.minutes = int(widget.get_text())
        self.update_text()

    def update_text(self, reset=False):
        '''
        Update the time phrase of the main window.
        '''
        if not reset:
            phrase = self.logic.clock.get_time_phrase(self.hours, self.minutes)
        else:
            phrase = 'Chasy'
        self.output_text.set_text(phrase)

    ##### MAIN MENU #####

    def on_help_about_activate(self, widget, data=None):
        self.about_dialogue.show()

    def on_file_save_as_activate(self, widget, data=None):
        self.file_chooser_window.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.file_open_button.hide()
        self.file_save_button.show()
        self.file_chooser_window.show()

    def on_file_save_activate(self, widget, data=None):
        self.on_file_save_as_activate(None)
#        self.logic.save_project()

    def on_file_open_activate(self, widget, data=None):
        self.file_chooser_window.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.file_open_button.show()
        self.file_save_button.hide()
        self.file_chooser_window.show()
#        self.logic.load_project()
#        self.cface_editor_window.hide()

    def on_tools_dump_full_activate(self, widget, data=None):
        text = '\n'.join(self.logic.clock.get_phrases_dump(True))
        self.__write_in_dump(text)
        self.dump_window.show()

    def on_tools_dump_textonly_activate(self, widget, data=None):
        text = '\n'.join(self.logic.clock.get_phrases_dump())
        self.__write_in_dump(text)
        self.dump_window.show()

    def on_tools_analysis_phrases_activate(self, widget, data=None):
        stats = self.logic.get_phrases_analysis()
        self.__write_in_dump(stats, 'courier')
        self.dump_window.show()

    def on_tools_blueprints_activate(self, widget, data=None):
        print('blueprints galore!')

    def on_tools_analysis_cface_activate(self, widget, data=None):
        print('analitical tools galore!')

    def on_edit_cface_activate(self, widget, data=None):
        self.__supersequence_heuristics_show_dialogue()
        self.logic.show_clockface(self.clockface_image,
                                  self.col_number_adjustment,
                                  self.update_clockface_stats)
        self.cface_editor_window.show()

    def on_edit_settings_activate(self, widget, data=None):
        self.settings_window.show()

    ##### DUMP WINDOW #####

    def on_close_dump_button_clicked(self, widget, data=None):
        self.dump_window.hide()

    ##### HEURISTICS WINDOW #####

    def on_stop_heuristic_button_clicked(self, widget, data=None):
        try:
            self.logic.halt_heuristic = True
            self.logic.supersequence.halt_heuristic = True
            self.logic.cface.halt_heuristic = True
        except AttributeError:
            pass  #some properties of logic aren't initialised immediately

    ##### CLOCKFACE EDITOR #####

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
        self.logic.vclock.update()

    def on_cfe_generate_code_clicked(self, widget, data=None):
        text = self.logic.supersequence.set_led_strings()
        self.__write_in_dump(text)
        self.dump_window.show()

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
        # The vclock might not be present if the clockface hasn't been
        # designed yet.
        try:
            tmp = self.vclock_cface.allocation
            self.logic.vclock.refresh_params(max_pixel_dimension=min(tmp.width,
                                                                     tmp.height))
            self.logic.vclock.update()
        except AttributeError:
            pass

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

    def on_vwc_italic_toggled(self, widget, data=None):
        self.logic.vclock.refresh_params(italic=widget.get_active())
        self.logic.vclock.update()

    def on_vwc_bold_toggled(self, widget, data=None):
        self.logic.vclock.refresh_params(bold=widget.get_active())
        self.logic.vclock.update()

    def on_save_screenshot_button_clicked(self, widget, data=None):
        self.logic.vclock.get_shot('svg')

    ##### PROJECT SETTINGS #####

    def on_file_new_activate(self, widget, data=None):
        self.settings_window.show()

    def on_sttng_module_lang_combo_changed(self, widget, data=None):
        self.__populate_clock_modules_combo()

    def on_sttng_module_name_combo_changed(self, widget, data=None):
        module = self.clock_modules_entries[widget.get_active()]
        cm = self.logic.clock_manager
        description = cm.get_module_description(module)
        self.sttng_mod_textbuffer.set_text(description)

    def on_setting_apply_button_clicked(self, widget, data=None):
        settings = {}
        # Clock module
        settings['clock'] = \
            self.clock_modules_entries[self.sttng_modname_combo.get_active()]
        # Clock resolution
        settings['resolution'] = \
            self.resolution_entries[self.sttng_accuracy_combo.get_active()]
        # Approximation method
        if self.sttng_approx_closest.get_active():
            tmp = 'closest'
        elif self.sttng_approx_last.get_active():
            tmp = 'last'
        settings['approx_method'] = tmp
        # Update project state and trigger message release
        self.logic.project.project_settings = settings
        self.logic.project.broadcast_change()
        self.settings_window.hide()

    ##### PROJECT SETTINGS #####

    def on_file_chooser_response(self, widget, data=None):
        widget.hide()
        fname = widget.get_filename()
        if data < 0:  # Cancel button or window closed
            return
        assert data in (1, 2)  # SAVE and OPEN opcodes respectively
        if data == 1:
            self.logic.project.save(fname)
        elif data == 2:
            self.logic.project.load(fname)

def run_as_script():
    '''Run this code if the file is executed as script.'''
    print('Module executed as script!')

if __name__ == '__main__':
    run_as_script()