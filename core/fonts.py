"""Fontu reģistrācija - latviešu burtu atbalsts.

Fonts (DejaVu Sans) tiek iekļauts pakas iekšienē mapē assets/fonts/.
Tas darbojas vienādi gan uz Windows, Linux, gan Android.

Vairs nelietojam matplotlib fontu meklēšanu - tas neder Android būvei.
"""
import os
import sys


# Globāls mainīgais lai citi moduļi varētu piekļūt fonta ceļam
LATVIAN_FONT_PATH = None
LATVIAN_FONT_BOLD_PATH = None


def _project_root() -> str:
    """Atgriež projekta saknes mapi (kur atrodas main.py)."""
    # core/fonts.py -> .. = projekta sakne
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _bundled_font_paths():
    """Atgriež (regular, bold) DejaVu Sans ceļus no assets/fonts/."""
    root = _project_root()
    fonts_dir = os.path.join(root, 'assets', 'fonts')
    regular = os.path.join(fonts_dir, 'DejaVuSans.ttf')
    bold = os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf')
    if os.path.exists(regular):
        return regular, bold if os.path.exists(bold) else regular
    return None, None


def _system_font_paths():
    """Atgriež sistēmas fontu kā rezerves variantu (lokālai izstrādei)."""
    if sys.platform.startswith('win'):
        windir = os.environ.get('WINDIR', 'C:\\Windows')
        fonts_dir = os.path.join(windir, 'Fonts')
        for r, b in [('segoeui.ttf', 'segoeuib.ttf'),
                     ('arial.ttf', 'arialbd.ttf')]:
            rp = os.path.join(fonts_dir, r)
            bp = os.path.join(fonts_dir, b)
            if os.path.exists(rp):
                return rp, bp if os.path.exists(bp) else rp
    elif sys.platform == 'darwin':
        for p in ['/System/Library/Fonts/Helvetica.ttc']:
            if os.path.exists(p):
                return p, p
    else:
        for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
            if os.path.exists(p):
                bold = p.replace('Sans.ttf', 'Sans-Bold.ttf')
                return p, bold if os.path.exists(bold) else p
    return None, None


def register_fonts():
    """Reģistrē fontu ar latviešu burtu atbalstu."""
    global LATVIAN_FONT_PATH, LATVIAN_FONT_BOLD_PATH

    print('=' * 60)
    print('[fonts] Saac fontu registreshanu...')

    # 1. mēģinājums: iekļautais fonts (assets/fonts/) - darbojas arī Android
    regular, bold = _bundled_font_paths()
    source = 'assets/fonts/DejaVuSans'

    # 2. mēģinājums: sistēmas fonts (tikai lokālai izstrādei)
    if not regular:
        regular, bold = _system_font_paths()
        source = 'sistemas fonts'

    if not regular:
        print('[fonts] BRIDINAJUMS: nevareja atrast nevienu fontu!')
        print('=' * 60)
        return False

    LATVIAN_FONT_PATH = regular
    LATVIAN_FONT_BOLD_PATH = bold

    try:
        from kivy.core.text import LabelBase

        # Pārreģistrē Roboto (KivyMD noklusējuma fonts)
        LabelBase.register(
            name='Roboto',
            fn_regular=regular,
            fn_bold=bold,
        )
        # Reģistrē arī ar nosaukumu 'LatvianFont' priekš tieša izsaukuma
        LabelBase.register(
            name='LatvianFont',
            fn_regular=regular,
            fn_bold=bold,
        )

        print(f'[fonts] Avots: {source}')
        print(f'[fonts] Regular: {regular}')
        print(f'[fonts] Bold:    {bold}')
        print('=' * 60)
        return True
    except Exception as e:
        print(f'[fonts] KLUDA: {e}')
        print('=' * 60)
        return False


def patch_kivymd_fonts():
    """Piespiež KivyMD theme_cls izmantot mūsu fontu visos font_styles."""
    if not LATVIAN_FONT_PATH:
        return False

    try:
        from kivy.core.text import LabelBase

        font_aliases = ['Roboto', 'RobotoLight', 'RobotoThin',
                        'RobotoMedium', 'RobotoBold', 'RobotoBlack']

        for alias in font_aliases:
            try:
                LabelBase.register(
                    name=alias,
                    fn_regular=LATVIAN_FONT_PATH,
                    fn_bold=LATVIAN_FONT_BOLD_PATH,
                )
            except Exception:
                pass

        print('[fonts] KivyMD font_styles parakstiti uz DejaVu Sans')
        return True
    except Exception as e:
        print(f'[fonts] KivyMD patch kluda: {e}')
        return False
