"""Pievienot/rediģēt grāmatas ekrāns."""
from datetime import date
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.pickers import MDDatePicker

from core.models import Book, STATUS_LABELS


class AddBookScreen(Screen):
    book_id = NumericProperty(0)  # 0 = jauna grāmata, citādi rediģē
    cover_path = StringProperty('')

    def on_enter_screen(self, book_id=0, prefill=None, **kwargs):
        """Tiek izsaukts, kad ekrāns kļūst aktīvs.
        prefill = dict ar laukiem no Open Library meklēšanas."""
        self.book_id = book_id or 0
        self._reset_form()

        if book_id:
            book = MDApp.get_running_app().db.get_book(book_id)
            if book:
                self._fill_from_book(book)
                self.ids.title_label.text = 'Rediģēt grāmatu'
                self.ids.delete_btn.disabled = False
        elif prefill:
            self._fill_from_dict(prefill)
            self.ids.title_label.text = 'Pievienot grāmatu'
            self.ids.delete_btn.disabled = True
        else:
            self.ids.title_label.text = 'Pievienot grāmatu'
            self.ids.delete_btn.disabled = True

    def _reset_form(self):
        ids = self.ids
        ids.title_input.text = ''
        ids.author_input.text = ''
        ids.isbn_input.text = ''
        ids.pages_input.text = ''
        ids.genre_input.text = ''
        ids.notes_input.text = ''
        ids.status_spinner.text = STATUS_LABELS['want_to_read']
        ids.rating_label.text = self._stars(0)
        ids.started_btn.text = 'Sākuma datums'
        ids.finished_btn.text = 'Beigu datums'
        self.cover_path = ''
        self._current_rating = 0
        self._started_date = None
        self._finished_date = None

    def _fill_from_book(self, book: Book):
        ids = self.ids
        ids.title_input.text = book.title
        ids.author_input.text = book.author or ''
        ids.isbn_input.text = book.isbn or ''
        ids.pages_input.text = str(book.pages) if book.pages else ''
        ids.genre_input.text = book.genre or ''
        ids.notes_input.text = book.notes or ''
        ids.status_spinner.text = book.status_label
        self._current_rating = book.rating
        ids.rating_label.text = self._stars(book.rating)
        self._started_date = book.started_date
        self._finished_date = book.finished_date
        if book.started_date:
            ids.started_btn.text = book.started_date
        if book.finished_date:
            ids.finished_btn.text = book.finished_date
        self.cover_path = book.cover_path or ''

    def _fill_from_dict(self, data: dict):
        ids = self.ids
        ids.title_input.text = data.get('title', '')
        ids.author_input.text = data.get('author', '')
        ids.isbn_input.text = data.get('isbn', '')
        if data.get('pages'):
            ids.pages_input.text = str(data['pages'])
        if data.get('subject'):
            subjects = data['subject']
            if subjects:
                ids.genre_input.text = subjects[0] if isinstance(subjects, list) else subjects
        self.cover_path = data.get('cover_path', '')

    @staticmethod
    def _stars(n: int) -> str:
        return '★' * n + '☆' * (5 - n)

    def set_rating(self, n: int):
        self._current_rating = n
        self.ids.rating_label.text = self._stars(n)

    def open_status_menu(self, caller):
        from kivymd.uix.menu import MDDropdownMenu
        items = [{'text': label,
                 'on_release': lambda s=status, l=label: self._set_status(s, l)}
                for status, label in STATUS_LABELS.items()]
        self.status_menu = MDDropdownMenu(caller=caller, items=items, width_mult=4)
        self.status_menu.open()

    def _set_status(self, status_key, label):
        self.ids.status_spinner.text = label
        self._status_key = status_key
        if hasattr(self, 'status_menu'):
            self.status_menu.dismiss()

    def open_started_picker(self):
        picker = MDDatePicker()
        picker.bind(on_save=lambda i, v, r: self._on_started(v))
        picker.open()

    def _on_started(self, value):
        self._started_date = value.isoformat()
        self.ids.started_btn.text = self._started_date

    def open_finished_picker(self):
        picker = MDDatePicker()
        picker.bind(on_save=lambda i, v, r: self._on_finished(v))
        picker.open()

    def _on_finished(self, value):
        self._finished_date = value.isoformat()
        self.ids.finished_btn.text = self._finished_date

    def save_book(self):
        ids = self.ids
        title = ids.title_input.text.strip()
        if not title:
            self._show_dialog('Nosaukums ir obligāts!')
            return

        # Statusa atslēga
        status_key = getattr(self, '_status_key', None)
        if not status_key:
            current_label = ids.status_spinner.text
            status_key = next((k for k, v in STATUS_LABELS.items()
                             if v == current_label), 'want_to_read')

        try:
            pages = int(ids.pages_input.text) if ids.pages_input.text.strip() else 0
        except ValueError:
            pages = 0

        book = Book(
            id=self.book_id if self.book_id else None,
            title=title,
            author=ids.author_input.text.strip(),
            isbn=ids.isbn_input.text.strip(),
            pages=pages,
            genre=ids.genre_input.text.strip(),
            status=status_key,
            rating=getattr(self, '_current_rating', 0),
            notes=ids.notes_input.text.strip(),
            cover_path=self.cover_path,
            started_date=self._started_date,
            finished_date=self._finished_date,
        )

        app = MDApp.get_running_app()
        if self.book_id:
            app.db.update_book(book)
        else:
            app.db.add_book(book)

        app.switch_to('library')

    def delete_book(self):
        if not self.book_id:
            return

        def confirm(*_):
            app = MDApp.get_running_app()
            app.db.delete_book(self.book_id)
            self.dialog.dismiss()
            app.switch_to('library')

        self.dialog = MDDialog(
            title='Dzēst grāmatu?',
            text='Šī darbība ir neatgriezeniska.',
            buttons=[
                MDFlatButton(text='Atcelt', on_release=lambda *_: self.dialog.dismiss()),
                MDFlatButton(text='Dzēst', on_release=confirm),
            ],
        )
        self.dialog.open()

    def _show_dialog(self, text):
        self.dialog = MDDialog(title='Brīdinājums', text=text,
            buttons=[MDFlatButton(text='OK',
                on_release=lambda *_: self.dialog.dismiss())])
        self.dialog.open()
