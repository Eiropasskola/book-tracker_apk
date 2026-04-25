"""Open Library meklēšanas ekrāns."""
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from threading import Thread
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage


class SearchResultCard(MDCard):
    def __init__(self, result_data, **kwargs):
        super().__init__(**kwargs)
        self.result_data = result_data
        self.orientation = 'horizontal'
        self.padding = dp(10)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(110)
        self.elevation = 1
        self.radius = [dp(8)]
        self.ripple_behavior = True

        ph = MDCard(size_hint_x=None, width=dp(60),
                   md_bg_color=(0.85, 0.85, 0.9, 1),
                   radius=[dp(4)], elevation=0)
        from kivymd.uix.label import MDIcon
        ph.add_widget(MDIcon(icon='book-open-variant',
                             halign='center', valign='center',
                             theme_text_color='Custom',
                             text_color=(0.4, 0.4, 0.5, 1),
                             font_size='32sp'))
        self.add_widget(ph)

        info = MDBoxLayout(orientation='vertical', spacing=dp(2))
        info.add_widget(MDLabel(text=result_data['title'],
                               font_style='Subtitle1', bold=True,
                               shorten=True, shorten_from='right'))
        info.add_widget(MDLabel(text=result_data['author'] or 'Nezināms',
                               font_style='Caption', theme_text_color='Secondary',
                               shorten=True))
        details = []
        if result_data.get('first_publish_year'):
            details.append(str(result_data['first_publish_year']))
        if result_data.get('isbn'):
            details.append(f"ISBN: {result_data['isbn'][:13]}")
        info.add_widget(MDLabel(text=' • '.join(details),
                               font_style='Caption', theme_text_color='Hint'))
        self.add_widget(info)

    def on_release(self):
        screen = MDApp.get_running_app().root.get_screen('search')
        screen.select_result(self.result_data)


class SearchScreen(Screen):
    def on_enter_screen(self, **kwargs):
        if self.ids:
            self.ids.search_input.text = ''
            self.ids.results_box.clear_widgets()
            self.ids.results_box.add_widget(MDLabel(
                text='Ievadi nosaukumu, autoru vai ISBN un piesit "Meklēt"',
                halign='center', theme_text_color='Hint',
                size_hint_y=None, height=dp(120)))

    def do_search(self):
        query = self.ids.search_input.text.strip()
        if not query:
            return
        self.ids.results_box.clear_widgets()
        self.ids.results_box.add_widget(MDLabel(
            text='Meklē...', halign='center', theme_text_color='Secondary',
            size_hint_y=None, height=dp(60)))

        # Meklēšana fona pavedienā lai neaizkaltētu UI
        Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query):
        app = MDApp.get_running_app()
        results = app.api.search(query, limit=20)
        Clock.schedule_once(lambda dt: self._show_results(results), 0)

    def _show_results(self, results):
        box = self.ids.results_box
        box.clear_widgets()
        if not results:
            box.add_widget(MDLabel(
                text='Nekas nav atrasts (vai nav interneta)',
                halign='center', theme_text_color='Hint',
                size_hint_y=None, height=dp(60)))
            return
        for r in results:
            box.add_widget(SearchResultCard(r))

    def select_result(self, result_data):
        """Lietotājs izvēlējās grāmatu - lejupielādē vāku un atver formu."""
        app = MDApp.get_running_app()

        # Lejupielādē vāku fonā
        def download():
            cover_path = app.api.download_cover(
                isbn=result_data.get('isbn', ''),
                cover_id=result_data.get('cover_id'),
                save_dir=app.covers_dir,
            )
            prefill = dict(result_data)
            prefill['cover_path'] = cover_path or ''
            Clock.schedule_once(lambda dt: app.switch_to('add_book', prefill=prefill), 0)

        Thread(target=download, daemon=True).start()
