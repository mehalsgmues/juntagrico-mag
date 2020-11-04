from datetime import datetime, timedelta
import drawSvg as draw
import colorsys
import math

from juntagrico.entity.share import Share

from mehalsgmues import settings


def date_from_get(request, name, default, date_format="%Y-%m-%d"):
    date = request.GET.get(name, None)
    if date is not None:
        return datetime.strptime(date, date_format)
    return default


def get_delivery_dates_of_month(delivery_weekday, relative_month):
    today = datetime.today()
    # get dates of next month if this month is half over.
    month = today.month + int(today.day > 15) + relative_month
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
    color = rgb_to_hex(colorsys.hls_to_rgb((-30 + 100 * progress) / 255, 74 / 255, 1))
    p = draw.Path(fill=color, **options)
    progress = min(progress, 0.99999)
    p.arc(0, 0, 0.7, 90 - 360 * progress, 90)
    p.arc(0, 0, 0.5, 90, 90 - 360 * progress, cw=True, includeL=True)
    p.Z()
    return p


def on_arc(r, prog, side='outer', size=0.047, lines=1):
    prog = prog - int(prog)
    return {
        'fontSize': size,
        'x': math.sin(prog * 2 * math.pi) * r,
        'y': math.cos(prog * 2 * math.pi) * r + size*((lines-1) - (lines if (side == 'outer') ^ (abs(prog - 0.5) > 0.25) else 0)),
        'text_anchor': 'start' if (side == 'outer') ^ (prog > 0.5) else 'end',
    }


def draw_share_progress():
    goal = int(getattr(settings, "SHARE_PROGRESS_GOAL", "0") or "1400")
    offset = int(getattr(settings, "SHARE_PROGRESS_OFFSET", "0") or "0")
    ordered = Share.objects.filter(cancelled_date__isnull=True).count() + offset
    ordered_progress = ordered/goal
    paid = Share.objects.filter(cancelled_date__isnull=True, paid_date__isnull=False).count() + offset
    paid_progress = paid/goal

    d = draw.Drawing(1.8, 1.5, origin='center')

    arrow = draw.Marker(-0.2, -0.5, 0.9, 0.5, scale=20, orient='auto')
    arrow.append(draw.Lines(-0.2, -0.5, 0, 0, -0.2, 0.5, 0.9, 0, fill='black', close=True))

    arc = draw.Path(stroke='black', stroke_width=0.002, fill_opacity=0, marker_end=arrow)
    arc.arc(0, 0, 0.6, 89, 94, cw=True)
    d.append(arc)

    d.append(progress_arc(ordered_progress, fill_opacity=0.5))
    d.append(progress_arc(paid_progress))

    # text center
    if goal > ordered:
        d.append(draw.Text('Noch', 0.1, 0, 0.3, center=True))
        d.append(draw.Text(str(goal-ordered), 0.3, 0, 0.12, center=True, font_weight='bold'))
        d.append(draw.Text('Anteilscheine', 0.09, 0, -0.1, center=True))
        # labels
        d.append(draw.Text(f'{ordered}\nbestellt', **on_arc(0.7, ordered_progress, lines=2)))
        d.append(draw.Text(f'{paid}\nbezahlt', **on_arc(0.5, paid_progress, 'inner', lines=2)))
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
