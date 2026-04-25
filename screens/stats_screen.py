"""Statistikas ekrāns ar grafikiem."""
from datetime import datetime
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image as KivyImage
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

from core import charts


class StatsScreen(Screen):
    def on_enter_screen(self, **kwargs):
        self.refresh()

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        if not self.ids:
            return
        app = MDApp.get_running_app()
        is_dark = app.theme_cls.theme_style == 'Dark'
        year = datetime.now().year

        box = self.ids.charts_box
        box.clear_widgets()

        # Gada mērķa progress
        goal = app.db.get_goal(year)
        if goal and goal.target_books > 0:
            current = app.db.finished_count_for_year(year)
            path = charts.chart_goal_progress(current, goal.target_books, year,
                                             unit='grāmatas', dark=is_dark)
            box.add_widget(self._chart_card(path, dp(180)))

        # Pa mēnešiem
        month_data = app.db.books_finished_by_month(year)
        path = charts.chart_books_per_month(month_data, year, dark=is_dark)
        box.add_widget(self._chart_card(path, dp(280)))

        # Žanri
        genre_data = app.db.books_by_genre()
        path = charts.chart_genre_pie(genre_data, dark=is_dark)
        box.add_widget(self._chart_card(path, dp(320)))

        # Vid. vērtējums
        rating_data = app.db.avg_rating_by_year()
        path = charts.chart_avg_rating(rating_data, dark=is_dark)
        box.add_widget(self._chart_card(path, dp(280)))

        # Kopējā statistika
        total_books = len(app.db.list_books(status='finished'))
        total_pages = app.db.pages_count_for_year(year)
        summary = MDCard(
            orientation='vertical', padding=dp(15), spacing=dp(5),
            size_hint_y=None, height=dp(110), elevation=1, radius=[dp(8)])
        summary.add_widget(MDLabel(text='Kopā', font_style='Subtitle1',
                                   bold=True, size_hint_y=None, height=dp(24)))
        summary.add_widget(MDLabel(text=f'Izlasītas: {total_books} grāmatas',
                                   theme_text_color='Secondary',
                                   size_hint_y=None, height=dp(20)))
        summary.add_widget(MDLabel(text=f'{year}. gadā: {total_pages} lapas',
                                   theme_text_color='Secondary',
                                   size_hint_y=None, height=dp(20)))
        box.add_widget(summary)

    @staticmethod
    def _chart_card(image_path: str, height) -> MDCard:
        card = MDCard(orientation='vertical', padding=dp(8),
                     size_hint_y=None, height=height,
                     elevation=1, radius=[dp(8)])
        card.add_widget(KivyImage(source=image_path, allow_stretch=True,
                                  keep_ratio=True))
        return card
