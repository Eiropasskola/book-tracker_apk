"""Grafiku ģenerēšana ar Pillow (bez matplotlib).

Matplotlib NEDARBOJAS uz python-for-android - kompilācija ir lēna un nestabila.
Šī versija izmanto Pillow, kas Android vidē darbojas lieliski.
"""
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

from core.fonts import LATVIAN_FONT_PATH, LATVIAN_FONT_BOLD_PATH


LV_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jūn',
             'Jūl', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']

# Krāsu palete
COLOR_PRIMARY = '#5E72E4'
COLOR_SUCCESS = '#2DCE89'
COLOR_WARN = '#FB6340'
COLOR_DANGER = '#F5365C'
PIE_PALETTE = ['#5E72E4', '#2DCE89', '#FB6340', '#F5365C',
               '#11CDEF', '#FFD600', '#8965E0', '#F3A4B5']


def _get_temp_path(name: str) -> str:
    return os.path.join(tempfile.gettempdir(), f'booktracker_{name}.png')


def _theme_colors(dark: bool):
    if dark:
        return {'bg': '#1E1E1E', 'fg': '#FFFFFF', 'grid': '#3A3A3A',
                'axis': '#888888'}
    return {'bg': '#FFFFFF', 'fg': '#222222', 'grid': '#E9ECEF',
            'axis': '#555555'}


def _font(size: int, bold: bool = False):
    """Ielādē fontu ar latviešu burtu atbalstu."""
    path = LATVIAN_FONT_BOLD_PATH if bold else LATVIAN_FONT_PATH
    try:
        if path:
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def _text_size(draw, text, font):
    """Pareizs teksta izmērs (saderīgs ar Pillow >= 9)."""
    try:
        x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
        return x1 - x0, y1 - y0
    except Exception:
        return draw.textsize(text, font=font)


def chart_books_per_month(data: dict, year: int, dark: bool = False) -> str:
    """Bāru grafiks: izlasītās grāmatas pa mēnešiem."""
    c = _theme_colors(dark)
    W, H = 800, 450
    img = Image.new('RGB', (W, H), c['bg'])
    d = ImageDraw.Draw(img)

    title_font = _font(20, bold=True)
    label_font = _font(13)
    value_font = _font(12, bold=True)

    title = f'Izlasītās grāmatas {year}. gadā'
    tw, th = _text_size(d, title, title_font)
    d.text(((W - tw) / 2, 15), title, fill=c['fg'], font=title_font)

    counts = [data.get(m, 0) for m in range(1, 13)]
    max_count = max(counts) if max(counts) > 0 else 1

    margin_l, margin_r, margin_t, margin_b = 60, 30, 60, 60
    chart_w = W - margin_l - margin_r
    chart_h = H - margin_t - margin_b
    bar_slot = chart_w / 12
    bar_w = bar_slot * 0.65

    # Y ass režģis
    for i in range(5):
        y = margin_t + chart_h * i / 4
        d.line([(margin_l, y), (W - margin_r, y)], fill=c['grid'], width=1)
        val = int(max_count * (4 - i) / 4)
        d.text((10, y - 7), str(val), fill=c['axis'], font=label_font)

    # Bāri
    for i, count in enumerate(counts):
        if count == 0:
            continue
        bh = (count / max_count) * chart_h
        x0 = margin_l + i * bar_slot + (bar_slot - bar_w) / 2
        y0 = margin_t + chart_h - bh
        x1 = x0 + bar_w
        y1 = margin_t + chart_h
        d.rectangle([x0, y0, x1, y1], fill=COLOR_PRIMARY)
        # Vērtība virs bāra
        vt = str(count)
        vw, vh = _text_size(d, vt, value_font)
        d.text((x0 + (bar_w - vw) / 2, y0 - vh - 4), vt,
               fill=c['fg'], font=value_font)

    # X ass etiķetes
    for i, name in enumerate(LV_MONTHS):
        x = margin_l + i * bar_slot + bar_slot / 2
        nw, nh = _text_size(d, name, label_font)
        d.text((x - nw / 2, margin_t + chart_h + 8),
               name, fill=c['axis'], font=label_font)

    path = _get_temp_path('per_month')
    img.save(path)
    return path


def chart_genre_pie(data: dict, dark: bool = False) -> str:
    """Riņķa diagramma: žanru sadalījums."""
    c = _theme_colors(dark)
    W, H = 700, 500
    img = Image.new('RGB', (W, H), c['bg'])
    d = ImageDraw.Draw(img)

    title_font = _font(20, bold=True)
    label_font = _font(13)

    title = 'Žanru sadalījums'
    tw, th = _text_size(d, title, title_font)
    d.text(((W - tw) / 2, 15), title, fill=c['fg'], font=title_font)

    if not data:
        msg = 'Vēl nav datu par žanriem'
        mw, mh = _text_size(d, msg, label_font)
        d.text(((W - mw) / 2, H / 2), msg, fill=c['axis'], font=label_font)
    else:
        cx, cy, r = 220, 270, 150
        total = sum(data.values()) or 1
        start = -90  # sākam augšā
        items = list(data.items())
        # PIL pieprasa float; rinda 0..n
        for i, (name, val) in enumerate(items):
            sweep = 360 * val / total
            color = PIE_PALETTE[i % len(PIE_PALETTE)]
            d.pieslice([cx - r, cy - r, cx + r, cy + r],
                       start, start + sweep, fill=color, outline=c['bg'])
            start += sweep

        # Leģenda labajā pusē
        lx, ly = 430, 130
        for i, (name, val) in enumerate(items):
            color = PIE_PALETTE[i % len(PIE_PALETTE)]
            d.rectangle([lx, ly, lx + 18, ly + 18], fill=color)
            pct = 100 * val / total
            label = f'{name}  ({pct:.0f}%)'
            d.text((lx + 26, ly + 1), label, fill=c['fg'], font=label_font)
            ly += 28
            if ly > H - 30:
                break

    path = _get_temp_path('genre_pie')
    img.save(path)
    return path


def chart_avg_rating(data: dict, dark: bool = False) -> str:
    """Līniju grafiks: vidējais vērtējums pa gadiem."""
    c = _theme_colors(dark)
    W, H = 800, 450
    img = Image.new('RGB', (W, H), c['bg'])
    d = ImageDraw.Draw(img)

    title_font = _font(20, bold=True)
    label_font = _font(13)
    value_font = _font(12, bold=True)

    title = 'Vidējais vērtējums pa gadiem'
    tw, th = _text_size(d, title, title_font)
    d.text(((W - tw) / 2, 15), title, fill=c['fg'], font=title_font)

    if not data:
        msg = 'Vēl nav vērtējumu'
        mw, mh = _text_size(d, msg, label_font)
        d.text(((W - mw) / 2, H / 2), msg, fill=c['axis'], font=label_font)
    else:
        years = sorted(data.keys())
        ratings = [data[y] for y in years]

        margin_l, margin_r, margin_t, margin_b = 60, 30, 60, 60
        chart_w = W - margin_l - margin_r
        chart_h = H - margin_t - margin_b

        # Y režģis 1..5
        for v in range(1, 6):
            y = margin_t + chart_h - (v / 5) * chart_h
            d.line([(margin_l, y), (W - margin_r, y)], fill=c['grid'], width=1)
            d.text((30, y - 7), str(v), fill=c['axis'], font=label_font)

        # Punkti un līnijas
        n = len(years)
        if n == 1:
            xs = [margin_l + chart_w / 2]
        else:
            xs = [margin_l + chart_w * i / (n - 1) for i in range(n)]
        ys = [margin_t + chart_h - (r / 5) * chart_h for r in ratings]

        for i in range(n - 1):
            d.line([(xs[i], ys[i]), (xs[i + 1], ys[i + 1])],
                   fill=COLOR_DANGER, width=3)

        for x, y, year, rating in zip(xs, ys, years, ratings):
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=COLOR_WARN)
            yt = str(year)
            yw, yh = _text_size(d, yt, label_font)
            d.text((x - yw / 2, margin_t + chart_h + 8),
                   yt, fill=c['axis'], font=label_font)
            rt = f'{rating:.1f}'
            rw, rh = _text_size(d, rt, value_font)
            d.text((x - rw / 2, y - rh - 12), rt, fill=c['fg'], font=value_font)

    path = _get_temp_path('avg_rating')
    img.save(path)
    return path


def chart_goal_progress(current: int, target: int, year: int,
                        unit: str = 'grāmatas', dark: bool = False) -> str:
    """Horizontāls progresa bārs gada mērķim."""
    c = _theme_colors(dark)
    W, H = 800, 240
    img = Image.new('RGB', (W, H), c['bg'])
    d = ImageDraw.Draw(img)

    title_font = _font(18, bold=True)
    label_font = _font(13)

    pct = min(100, (current / target * 100) if target > 0 else 0)
    color = COLOR_SUCCESS if pct >= 100 else COLOR_PRIMARY if pct >= 50 else COLOR_WARN

    title = f'{year}. g. mērķis: {current} / {target} {unit} ({pct:.0f}%)'
    tw, th = _text_size(d, title, title_font)
    d.text(((W - tw) / 2, 25), title, fill=c['fg'], font=title_font)

    # Bāra fons
    bx0, bx1 = 60, W - 60
    by0, by1 = 110, 150
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=12, fill=c['grid'])

    # Aizpildījums
    fill_x = bx0 + (bx1 - bx0) * pct / 100
    if fill_x > bx0 + 12:
        d.rounded_rectangle([bx0, by0, fill_x, by1], radius=12, fill=color)

    # Atzīmes 0/25/50/75/100
    for v in [0, 25, 50, 75, 100]:
        x = bx0 + (bx1 - bx0) * v / 100
        d.line([(x, by1 + 4), (x, by1 + 12)], fill=c['axis'], width=1)
        t = f'{v}%'
        tw, th = _text_size(d, t, label_font)
        d.text((x - tw / 2, by1 + 16), t, fill=c['axis'], font=label_font)

    path = _get_temp_path(f'goal_{unit}')
    img.save(path)
    return path
