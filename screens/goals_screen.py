"""Lasīšanas mērķu ekrāns."""
from datetime import datetime
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from core.models import Goal


class GoalsScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh()

    def on_enter_screen(self, **kwargs):
        self.refresh()

    def refresh(self):
        if not self.ids:
            return
        app = MDApp.get_running_app()
        year = datetime.now().year

        goal = app.db.get_goal(year)
        finished = app.db.finished_count_for_year(year)
        pages = app.db.pages_count_for_year(year)

        if goal:
            self.ids.year_label.text = f'{year}. gada mērķis'
            self.ids.target_books_input.text = str(goal.target_books)
            self.ids.target_pages_input.text = str(goal.target_pages or 0)

            books_pct = (finished / goal.target_books * 100) if goal.target_books > 0 else 0
            pages_pct = (pages / goal.target_pages * 100) if goal.target_pages > 0 else 0

            self.ids.books_progress.value = min(100, books_pct)
            self.ids.pages_progress.value = min(100, pages_pct)
            self.ids.books_status.text = (
                f'{finished} / {goal.target_books} grāmatas ({books_pct:.0f}%)')
            self.ids.pages_status.text = (
                f'{pages} / {goal.target_pages} lapas ({pages_pct:.0f}%)'
                if goal.target_pages else f'{pages} lapas (mērķis nav uzstādīts)')

            # Pārbaude vai atpaliek
            day_of_year = datetime.now().timetuple().tm_yday
            expected_pct = (day_of_year / 365) * 100
            if books_pct < expected_pct - 5 and goal.target_books > 0:
                self.ids.warning_label.text = (
                    f'! Šobrīd vajadzētu būt {expected_pct:.0f}% - mazliet atpaliec')
            elif books_pct >= 100:
                self.ids.warning_label.text = 'Mērķis sasniegts!'
            else:
                self.ids.warning_label.text = 'Lielisks temps!'
        else:
            self.ids.year_label.text = f'{year}. gada mērķis (vēl nav)'
            self.ids.target_books_input.text = ''
            self.ids.target_pages_input.text = ''
            self.ids.books_progress.value = 0
            self.ids.pages_progress.value = 0
            self.ids.books_status.text = f'Izlasītas: {finished}'
            self.ids.pages_status.text = f'Lapas: {pages}'
            self.ids.warning_label.text = ''

    def save_goal(self):
        try:
            target_books = int(self.ids.target_books_input.text or 0)
            target_pages = int(self.ids.target_pages_input.text or 0)
        except ValueError:
            self._show_error('Lūdzu ievadi skaitļus!')
            return

        if target_books < 0 or target_pages < 0:
            self._show_error('Mērķiem jābūt pozitīviem!')
            return

        app = MDApp.get_running_app()
        year = datetime.now().year
        app.db.set_goal(Goal(year=year, target_books=target_books,
                            target_pages=target_pages))
        self.refresh()
        self._show_dialog('Mērķis saglabāts!')

    def _show_dialog(self, text):
        self.dialog = MDDialog(title='', text=text,
            buttons=[MDFlatButton(text='OK',
                on_release=lambda *_: self.dialog.dismiss())])
        self.dialog.open()

    def _show_error(self, text):
        self.dialog = MDDialog(title='Kļūda', text=text,
            buttons=[MDFlatButton(text='OK',
                on_release=lambda *_: self.dialog.dismiss())])
        self.dialog.open()
