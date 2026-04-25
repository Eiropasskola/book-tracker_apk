"""Bibliotēkas ekrāns - galvenais saraksts ar filtriem."""
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton
from kivymd.uix.fitimage import FitImage

from core.models import STATUS_LABELS


class BookCard(MDCard):
    """Kartiņa vienai grāmatai sarakstā."""
    book_id = NumericProperty(0)
    title = StringProperty('')
    author = StringProperty('')
    status = StringProperty('')
    rating = NumericProperty(0)
    cover = StringProperty('')

    def __init__(self, book, **kwargs):
        super().__init__(**kwargs)
        self.book_id = book.id
        self.title = book.title
        self.author = book.author or 'Nezināms autors'
        self.status = book.status_label
        self.rating = book.rating
        self.cover = book.cover_path or ''

        self.orientation = 'horizontal'
        self.padding = dp(10)
        self.spacing = dp(12)
        self.size_hint_y = None
        self.height = dp(120)
        self.elevation = 1
        self.radius = [dp(8)]
        self.ripple_behavior = True

        # Vāks
        if self.cover:
            from os.path import isfile
            if isfile(self.cover):
                cover_widget = FitImage(source=self.cover,
                                       size_hint_x=None, width=dp(70),
                                       radius=[dp(4)])
            else:
                cover_widget = self._placeholder()
        else:
            cover_widget = self._placeholder()
        self.add_widget(cover_widget)

        # Teksts
        info = MDBoxLayout(orientation='vertical', spacing=dp(2))
        info.add_widget(MDLabel(text=self.title, font_style='Subtitle1',
                               bold=True, shorten=True, shorten_from='right'))
        info.add_widget(MDLabel(text=self.author, font_style='Caption',
                               theme_text_color='Secondary',
                               shorten=True, shorten_from='right'))
        info.add_widget(MDLabel(text=self.status, font_style='Caption',
                               theme_text_color='Hint'))
        if self.rating > 0:
            stars = '★' * self.rating + '☆' * (5 - self.rating)
            info.add_widget(MDLabel(text=stars, font_style='Caption',
                                   theme_text_color='Custom',
                                   text_color=(1, 0.7, 0, 1)))
        self.add_widget(info)

    def _placeholder(self):
        from kivymd.uix.label import MDIcon
        ph = MDCard(size_hint_x=None, width=dp(70),
                   md_bg_color=(0.85, 0.85, 0.9, 1),
                   radius=[dp(4)], elevation=0)
        ph.add_widget(MDIcon(icon='book-open-variant',
                             halign='center', valign='center',
                             theme_text_color='Custom',
                             text_color=(0.4, 0.4, 0.5, 1),
                             font_size='40sp'))
        return ph

    def on_release(self):
        MDApp.get_running_app().switch_to('add_book', book_id=self.book_id)


class LibraryScreen(Screen):
    current_filter = StringProperty('all')
    current_search = StringProperty('')

    def on_pre_enter(self, *args):
        self.refresh()

    def on_enter_screen(self, **kwargs):
        self.refresh()

    def refresh(self):
        if not self.ids:
            return
        app = MDApp.get_running_app()
        status = None if self.current_filter == 'all' else self.current_filter
        search = self.current_search if self.current_search else None
        books = app.db.list_books(status=status, search=search)

        list_box = self.ids.book_list
        list_box.clear_widgets()

        if not books:
            empty = MDLabel(
                text='Sāc savu bibliotēku!\nPieskaries "+" lai pievienotu grāmatu.',
                halign='center', valign='center',
                theme_text_color='Hint',
                size_hint_y=None, height=dp(200))
            list_box.add_widget(empty)
            return

        for book in books:
            list_box.add_widget(BookCard(book))

    def set_filter(self, filter_value: str):
        self.current_filter = filter_value
        self.refresh()

    def on_search_text(self, text: str):
        self.current_search = text.strip()
        self.refresh()

    def open_filter_menu(self, caller):
        items = [
            {'text': 'Visas grāmatas', 'on_release': lambda: self._set_and_close('all')},
        ] + [
            {'text': label, 'on_release': lambda s=status: self._set_and_close(s)}
            for status, label in STATUS_LABELS.items()
        ]
        self.menu = MDDropdownMenu(caller=caller, items=items, width_mult=4)
        self.menu.open()

    def _set_and_close(self, value):
        self.set_filter(value)
        if hasattr(self, 'menu'):
            self.menu.dismiss()

    def open_add_options(self, caller):
        items = [
            {'text': 'Meklēt Open Library',
             'leading_icon': 'magnify',
             'on_release': lambda: self._nav_and_close('search')},
            {'text': 'Pievienot manuāli',
             'leading_icon': 'pencil',
             'on_release': lambda: self._nav_and_close('add_book')},
        ]
        self.add_menu = MDDropdownMenu(caller=caller, items=items, width_mult=4)
        self.add_menu.open()

    def _nav_and_close(self, screen):
        if hasattr(self, 'add_menu'):
            self.add_menu.dismiss()
        MDApp.get_running_app().switch_to(screen)
