import base64
import datetime
import re

from django.core.management.base import BaseCommand

from juntagrico.entity.jobs import Job

import quopri
import ssl

from imapclient import IMAPClient

from mehalsgmues import settings
from mehalsgmues.models import AccessInformation


class Command(BaseCommand):

    def handle(self, *args, **options):

        ssl_context = ssl.create_default_context()

        # don't check if certificate hostname doesn't match target hostname
        ssl_context.check_hostname = False

        # don't check if the certificate is trusted by a certificate authority
        ssl_context.verify_mode = ssl.CERT_NONE

        with IMAPClient(settings.BIKE_CODE_HOST, ssl_context=ssl_context) as server:
            server.login(settings.BIKE_CODE_USERNAME,
                         settings.BIKE_CODE_PASSWORD)
            server.select_folder('INBOX')
            # print('%d messages in INBOX' % select_info[b'EXISTS'])
            # messages = server.search(['FROM', ''])

            # Search for all messages in the inbox
            message_ids = server.search(['ALL'])

            # Fetch and process each message
            for message_id in message_ids:
                # Fetch the message data
                message_data = server.fetch(message_id, ['BODY[]'])
                raw_message = message_data[message_id][b'BODY[]']
                html_content = raw_message.decode('utf-8')

                if 'Subject: =?utf-8?B?UmVzZXJ2aWVydW5nIEUtQmlrZSAxIHVuZCA1IGbDvHIgMjAyNg==?=' in html_content:
                    text = self.find_substring_between_tags(
                        html_content,
                        'Content-Type: text/plain; charset="utf-8"\r\nContent-Transfer-Encoding: base64\r\n\r\n',
                        '\r\n\r\n'
                    )
                    plain_text = base64.b64decode(text).decode('utf-8')
                    codes = plain_text.split('Flyer 5\r\n')[1]
                    matches = re.compile('(\d{2}).(\d{2}).\s*=\s*(\d{4})\s*=\s*(\d{4})').findall(codes)
                    for match in matches:
                        date = datetime.date(2026, int(match[1]), int(match[0]))
                        jobs = Job.objects.filter(
                            recuringjob__type__id=settings.BIKE_CODE_JOB_TYPE, time__date=date)
                        if jobs:
                            AccessInformation.objects.update_or_create(
                                job=jobs[0], name='Flyer 1', defaults={"code": match[2]})
                            AccessInformation.objects.update_or_create(
                                job=jobs[0], name='Flyer 5', defaults={"code": match[3]})

                else:
                    vehicle = self.find_substring_between_tags(
                        html_content, "Deine_Reservation_f=C3=BCr_", "_in_der_Sie")
                    if vehicle is not None:
                        vehicle = quopri.decodestring(vehicle.encode()).decode()

                    code = self.find_substring_between_tags(html_content,
                                                            "Mit dem Code =C2=AB", "=C2=BB")
                    date = self.find_substring_between_tags(html_content, "<li>Datum: ",
                                                            "</li>")

                    if date is None:
                        # print("No code extracted.")
                        continue

                    date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
                    vehicle = vehicle.replace("_", " ")

                    # print(vehicle, code, date)

                    jobs = Job.objects.filter(
                        recuringjob__type__id=settings.BIKE_CODE_JOB_TYPE, time__date=date)
                    if jobs:
                        AccessInformation.objects.update_or_create(
                            job=jobs[0], name=vehicle, defaults={"code": code})

    def find_substring_between_tags(self, text, start_tag, end_tag):
        start_index = text.find(start_tag)
        if start_index == -1:
            return None
        start_index += len(start_tag)

        end_index = text.find(end_tag, start_index)
        if end_index == -1:
            return None

        return text[start_index:end_index]
