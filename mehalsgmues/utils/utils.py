from datetime import datetime, timedelta
import drawSvg as draw
import colorsys
import math

import requests
from django.utils import timezone
from juntagrico.entity.share import Share

from mehalsgmues import settings


def date_from_get(request, name, default, date_format="%Y-%m-%d"):
    date = request.GET.get(name, None)
    if date is not None:
        return datetime.strptime(date, date_format).date()
    year = request.GET.get(name + '_year', None)
    if year is not None:
        month = request.GET.get(name + '_month', 1)
        day = request.GET.get(name + '_day', 1)
        return datetime(int(year), int(month), int(day)).date()
    return default


def get_delivery_dates_of_month(delivery_weekday, relative_month):
    today = datetime.today()
    # get dates of next month if this month is half over.
    month = (today.month + int(today.day > 15) + relative_month - 1) % 12 + 1
    date = datetime(today.year, month, 1)
    next_delivery = date + timedelta(days=(delivery_weekday - 1 - date.weekday()) % 7)
    yield next_delivery
    while True:
        next_delivery = next_delivery + timedelta(days=7)
        if next_delivery.month == month:
            yield next_delivery
        else:
            break


def rgb_to_hex(rgb):
    return '#' + ''.join('{:02X}'.format(int(a * 255)) for a in rgb)


def progress_arc(progress, **options):
    # Draw a shape to fill with the gradient
    if 'fill' not in options:
        options['fill'] = rgb_to_hex(colorsys.hls_to_rgb((-30 + 100 * progress) / 255, 74 / 255, 1))
    p = draw.Path(**options)
    progress = min(progress, 0.99999)
    p.arc(0, 0, 0.7, 90 - 360 * progress, 90)
    p.arc(0, 0, 0.5, 90, 90 - 360 * progress, cw=True, includeL=True)
    p.Z()
    return p


def on_arc(r, prog, side='outer', size=0.047):
    prog = prog - int(prog)
    return {
        'fontSize': size,
        'x': math.sin(prog * 2 * math.pi) * r,
        'y': math.cos(prog * 2 * math.pi) * r,
        'text_anchor': 'start' if (side == 'outer') ^ (prog > 0.5) else 'end',
        'valign': 'top' if (side == 'outer') ^ (abs(prog - 0.5) > 0.25) else 'bottom'
    }


def draw_share_progress():
    goal = int(getattr(settings, "SHARE_PROGRESS_GOAL", "10") or "10")
    offset = int(getattr(settings, "SHARE_PROGRESS_OFFSET", "0") or "0")
    baseline = int(getattr(settings, "SHARE_PROGRESS_BASELINE", "0") or "0")
    baseline_progress = baseline / goal
    ordered = Share.objects.filter(cancelled_date__isnull=True).count() + offset
    ordered_progress = ordered / goal
    paid = Share.objects.filter(cancelled_date__isnull=True, paid_date__isnull=False).count() + offset
    paid_progress = paid / goal

    d = draw.Drawing(1.8, 1.6, origin='center')

    arrow = draw.Marker(-0.2, -0.5, 0.9, 0.5, scale=20, orient='auto')
    arrow.append(draw.Lines(-0.2, -0.5, 0, 0, -0.2, 0.5, 0.9, 0, fill='black', close=True))

    arc = draw.Path(stroke='black', stroke_width=0.002, fill_opacity=0, marker_end=arrow)
    arc.arc(0, 0, 0.6, 89, 94, cw=True)
    d.append(arc)

    d.append(draw.Text(f'{goal}', **on_arc(0.63, 0.99)))

    d.append(progress_arc(ordered_progress, fill_opacity=0.5))
    d.append(progress_arc(paid_progress))
    if baseline > 0:
        d.append(progress_arc(baseline_progress, fill='#083c00'))

    # text center
    if goal > ordered:
        d.append(draw.Text('Noch', 0.1, 0, 0.3, center=True))
        d.append(draw.Text(str(goal - ordered), 0.3, 0, 0.12, center=True, font_weight='bold'))
        d.append(draw.Text('Anteilscheine', 0.09, 0, -0.1, center=True))
        # labels
        d.append(draw.Text(f'{ordered-baseline} neue\nbestellt', **on_arc(0.7, ordered_progress)))
        d.append(draw.Text(f'{paid-baseline} neue\nbezahlt', **on_arc(0.5, paid_progress, 'inner')))
        if baseline > 0:
            d.append(draw.Text(f'{baseline}\nbisher', fill='white', **on_arc(0.5, baseline_progress - 0.025)))
    else:
        d.append(draw.Text('Wir haben es', 0.09, 0, 0.14, center=True))
        d.append(draw.Text('Geschafft!', 0.18, 0, 0, center=True, font_weight='bold'))

    # Display
    d.setRenderSize(w='100%', h='100%')
    svg = d.asSvg()
    return svg[:-6] + """<style type="text/css">
        @font-face {
            font-family: 'Quicksand';
            src: url('/static/fonts/Quicksand-Regular.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }

        @font-face {
            font-family: 'Quicksand';
            src: url('/static/fonts/Quicksand-Light.ttf') format('truetype');
            font-weight: lighter;
            font-style: normal;
        }

        @font-face {
            font-family: 'Quicksand';
            src: url('/static/fonts/Quicksand-Bold.ttf') format('truetype');
            font-weight: bold;
            font-style: normal;
        }

        svg {
            font-family: "Quicksand", monospace;
        }
    </style>
    </svg>
    """


def forum_notifications(user):
    cache = forum_notifications.cache.get(user, None)
    if cache and cache[0] + timedelta(minutes=5) > timezone.now():
        return cache[1]

    base = "https://forum.mehalsgmues.ch/"
    method = base + "u/by-external/" + str(user.id) + ".json"
    headers = {
        'Api-Key': getattr(settings, "DISCOURSE_API_KEY", ""),
        'Api-Username': 'system'
    }
    response = requests.get(method, headers=headers)
    if response:
        try:
            username = response.json()['user']['username']
        except (ValueError, KeyError):
            forum_notifications.cache[user] = (timezone.now(), None)
            return None
        # now with the username get notifications
        method = base + "session/current.json"
        headers['Api-Username'] = username
        response = requests.get(method, headers=headers)
        if response:
            try:
                current_user = response.json()['current_user']
                notifications = current_user['unread_notifications'] + current_user[
                    'unread_high_priority_notifications']
                forum_notifications.cache[user] = (timezone.now(), notifications)
                return notifications
            except (ValueError, KeyError):
                forum_notifications.cache[user] = (timezone.now(), None)


forum_notifications.cache = {}
