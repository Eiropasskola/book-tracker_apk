"""Iestatījumu ekrāns - tēma, eksports."""
import os
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from core import exporter


class SettingsScreen(Screen):
    def on_pre_enter(self, *args):
        if self.ids:
            app = MDApp.get_running_app()
            self.ids.theme_switch.active = (app.theme_cls.theme_style == 'Dark')

    def toggle_theme(self, is_active: bool):
        app = MDApp.get_running_app()
        new_theme = 'Dark' if is_active else 'Light'
        app.theme_cls.theme_style = new_theme
        app.db.set_setting('theme', new_theme)

    def export_csv(self):
        app = MDApp.get_running_app()
        books = app.db.list_books()
        if not books:
            self._show_dialog('Nav datu', 'Bibliotēkā vēl nav grāmatu.')
            return
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(app.data_dir, f'books_export_{timestamp}.csv')
        try:
            exporter.export_csv(books, path)
            self._show_dialog('Eksportēts!', f'Saglabāts:\n{path}')
        except Exception as e:
            self._show_dialog('Kļūda', str(e))

    def export_json(self):
        app = MDApp.get_running_app()
        books = app.db.list_books()
        goals = app.db.list_goals()
        if not books and not goals:
            self._show_dialog('Nav datu', 'Bibliotēkā vēl nav datu.')
            return
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(app.data_dir, f'books_export_{timestamp}.json')
        try:
            exporter.export_json(books, goals, path)
            self._show_dialog('Eksportēts!', f'Saglabāts:\n{path}')
        except Exception as e:
            self._show_dialog('Kļūda', str(e))

    def _show_dialog(self, title, text):
        self.dialog = MDDialog(title=title, text=text,
            buttons=[MDFlatButton(text='OK',
                on_release=lambda *_: self.dialog.dismiss())])
        self.dialog.open()
