"""Grāmatu izsekotājs - galvenais ieejas punkts."""
import os
import sys

# Lai darbotos arī no PyInstaller bundle
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

# ===== KRITISKI: fonti jāreģistrē VISPĀRMS, pirms jebkura Kivy importa =====
from core.fonts import register_fonts, patch_kivymd_fonts
register_fonts()

from kivy.config import Config
Config.set('graphics', 'width', '420')
Config.set('graphics', 'height', '780')
Config.set('graphics', 'minimum_width', '360')
Config.set('graphics', 'minimum_height', '600')

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp

# Pēc KivyMD importēšanas pārreģistrē fontus arī tā font_styles
patch_kivymd_fonts()

from core.database import Database
from core.api_client import OpenLibraryClient

from screens.library_screen import LibraryScreen
from screens.add_book_screen import AddBookScreen
from screens.search_screen import SearchScreen
from screens.stats_screen import StatsScreen
from screens.goals_screen import GoalsScreen
from screens.settings_screen import SettingsScreen


def app_data_dir() -> str:
    """Atgriež mapi datu glabāšanai (cross-platform)."""
    if 'ANDROID_ARGUMENT' in os.environ:
        from android.storage import app_storage_path  # type: ignore
        return app_storage_path()
    if sys.platform.startswith('win'):
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif sys.platform == 'darwin':
        base = os.path.expanduser('~/Library/Application Support')
    else:
        base = os.path.expanduser('~/.local/share')
    path = os.path.join(base, 'BookTracker')
    os.makedirs(path, exist_ok=True)
    return path


class BookTrackerApp(MDApp):
    def build(self):
        self.title = 'Grāmatu izsekotājs'

        # Datu mape
        self.data_dir = app_data_dir()
        self.covers_dir = os.path.join(self.data_dir, 'covers')
        os.makedirs(self.covers_dir, exist_ok=True)

        # Datubāze un API
        db_path = os.path.join(self.data_dir, 'books.db')
        self.db = Database(db_path)
        self.api = OpenLibraryClient()

        # Tēma no iestatījumiem
        theme = self.db.get_setting('theme', 'Light')
        self.theme_cls.theme_style = theme  # 'Light' vai 'Dark'
        self.theme_cls.primary_palette = 'Indigo'
        self.theme_cls.accent_palette = 'Orange'

        # Ielādē .kv failus
        kv_dir = os.path.join(os.path.dirname(__file__), 'kv')
        if os.path.isdir(kv_dir):
            for filename in sorted(os.listdir(kv_dir)):
                if filename.endswith('.kv'):
                    Builder.load_file(os.path.join(kv_dir, filename))

        # Ekrānu menedžeris
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(LibraryScreen(name='library'))
        sm.add_widget(AddBookScreen(name='add_book'))
        sm.add_widget(SearchScreen(name='search'))
        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(GoalsScreen(name='goals'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def switch_to(self, screen_name: str, **kwargs):
        sm = self.root
        if screen_name in [s.name for s in sm.screens]:
            screen = sm.get_screen(screen_name)
            if hasattr(screen, 'on_enter_screen'):
                screen.on_enter_screen(**kwargs)
            sm.current = screen_name


if __name__ == '__main__':
    BookTrackerApp().run()
