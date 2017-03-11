#! /usr/bin/python3.4
# -*- coding: utf-8 -*-
#
# program.py
#

import os
import sys

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.properties import ObjectProperty
from kivy.utils import get_hex_from_color

from libs.uix import customsettings
from libs.uix.dialogs import dialog

from libs.uix.kv.activity.baseclass.startscreen import StartScreen

from libs import programdata as data
from libs import programclass as _class

from kivymd.theming import ThemeManager
from kivymd.navigationdrawer import NavigationDrawer


class NavDrawer(NavigationDrawer):
    events_callback = ObjectProperty()


class Program(App, _class.ShowPlugin, _class.ShowAbout, _class.ShowLicense):
    '''Функционал программы.'''

    settings_cls = customsettings.CustomSettings
    customsettings.TEXT_INPUT = data.string_lang_enter_value
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Teal'

    def __init__(self, **kvargs):
        super(Program, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)

        self.data = data
        self.open_exit_dialog = None
        self.load_all_kv_files('{}/libs/uix/kv'.format(self.directory))
        self.load_all_kv_files(
            '{}/libs/uix/kv/activity'.format(self.directory)
        )

    def build_config(self, config):
        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'Русский')
        config.setdefault('General', 'theme', 'default')

    def build_settings(self, settings):
        with open('{}/data/settings/general.json'.format(
                data.prog_path), 'r') as settings_json:
            settings.add_json_panel(data.string_lang_settings, self.config,
                data=settings_json.read().format(
                    language=data.string_lang_setting_language,
                    title=data.string_lang_setting_language_title,
                    desc=data.string_lang_setting_language_desc,
                    russian=data.string_lang_setting_language_russian,
                    english=data.string_lang_setting_language_english))

    def build(self):
        self.use_kivy_settings = False
        self.title = data.string_lang_title  # заголовок окна программы
        self.icon = 'data/images/logo.png'  # иконка окна программы

        self.config = ConfigParser()
        self.config.read('{}/program.ini'.format(data.prog_path))

        # Главный экран программы.
        self.screen = StartScreen(events_callback=self.events_program)
        self.nav_drawer = NavDrawer(title=data.string_lang_menu)

        return self.screen

    def events_program(self, *args):
        '''Вызывается при выборе одного из пунктов меню программы.'''

        if len(args) == 2:  # нажата ссылка
            event = args[1]
        else:  # нажата кнопка программы
            try:
                _args = args[0]
                event = _args if isinstance(_args, str) else _args.id
            except AttributeError:  # нажата кнопка девайса
                event = args[1]

        if data.PY2:
            if isinstance(event, unicode):
                event = event.encode('utf-8')

        if event == data.string_lang_settings:
            self.open_settings()
        elif event == data.string_lang_exit_key:
            self.exit_program()
        elif event == data.string_lang_license:
            self.show_license()
        elif event == data.string_lang_plugin:
            self.show_plugins()
        elif event in (1001, 27):
            self.back_screen(event)
        elif event == 'About':
            self.show_about()

        return True

    def back_screen(self, event):
        '''Менеджер экранов.'''

        # Нажата BackKey на главном экране.
        if self.screen.ids.screen_manager.current == '':
            if event in (1001, 27):
                self.exit_program()
            return
        if len(self.screen.ids.screen_manager.screens) != 1:
            self.screen.ids.screen_manager.screens.pop()
        self.screen.ids.screen_manager.current = \
            self.screen.ids.screen_manager.screen_names[-1]
        self.set_current_item_tabbed_panel(
            data.theme_text_color, get_hex_from_color(
                data.color_action_bar
            )
        )

    def exit_program(self, *args):
        def close_dialog():
            self.open_exit_dialog.dismiss()
            self.open_exit_dialog = None

        if self.open_exit_dialog:
            return

        self.open_exit_dialog = dialog(
            text=data.string_lang_exit, title=self.title, dismiss=False,
            buttons=[
                [data.string_lang_yes, lambda *x: sys.exit(0)],
                [data.string_lang_no, lambda *x: close_dialog()]
            ]
        )

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            if kv_file in ('bugreporter.kv', '__init__.py') or \
                    os.path.isdir('{}/{}'.format(directory_kv_files, kv_file)):
                continue
            Builder.load_file('{}/{}'.format(directory_kv_files, kv_file))

    def on_config_change(self, config, section, key, value):
        '''Вызывается при выборе одного из пункта настроек программы.'''

        if key == 'language':
            if not os.path.exists('{}/data/language/{}.txt'.format(
                    self.directory, data.select_locale[value])):
                dialog(
                    text=data.string_lang_not_locale.format(
                        data.select_locale[value]
                    ),
                    title=self.title
                )
                config.set(section, key, data.old_language)

                config.write()
                self.close_settings()

    def on_pause(self):
        '''Ставит приложение на 'паузу' при выхоже из него.
        В противном случае запускает программу заново'''

        return True
