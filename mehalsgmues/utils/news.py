import requests

from mehalsgmues import settings


def get_recent_posts():
    base = "https://news.mehalsgmues.ch/wp-json/wp/v2/"
    method = base + "posts?_fields=content.rendered,title&categories=2"
    response = requests.get(method, auth=(settings.WP_USER, settings.WP_PASSWORD))
    if response:
        html = ''
        for post in response.json():
            html += '<h2 class="wp-title">' + post['title']['rendered'] + "</h2>"
            html += post['content']['rendered']
        return html
