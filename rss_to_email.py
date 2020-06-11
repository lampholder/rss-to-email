import os
import sys
import sqlite3

import boto3
import requests
import feedparser

from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

URL = os.environ['FEED_URL']
USERNAME = os.environ['BASIC_AUTH_USERNAME']
PASSWORD = os.environ['BASIC_AUTH_PASSWORD']
FROM = os.environ['FROM_EMAIL_ADDRESS']
TO = os.environ['TO_EMAIL_ADDRESS']
AWS_ACCESS_KEY_ID = os.environ['SES_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['SES_AWS_SECRET_ACCESS_KEY']
AWS_REGION_NAME = os.environ['SES_AWS_REGION_NAME']

def html_to_text(html):
    return ' '.join(BeautifulSoup(html, features="html.parser").get_text().split())

class Tracker():

    def __init__(self):
        self.db = sqlite3.connect('./state/seen.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('create table if not exists seen (guid text)')
        self.db.commit()

    def seen_before(self, guid):
        self.cursor.execute('select * from seen where guid = ?', [guid])
        return len(self.cursor.fetchall()) > 0

    def mark_seen(self, guid):
        self.cursor.execute('insert into seen values(?)', [guid])
        self.db.commit()

class Emailer():

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region_name):
        self.emailer = boto3.client(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region_name,
                service_name='ses',
                use_ssl=True)

    def send_email(self, from_address, destination, subject, body):
        self.emailer.send_email(
            Source=from_address,
            Destination={
                'ToAddresses': [
                    destination
                ]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body
                    }
                }
            }
        )

tracker = Tracker()
emailer = Emailer(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME)

request = requests.get(URL, auth=HTTPBasicAuth(USERNAME, PASSWORD))
feed = feedparser.parse(request.text)
new_entries = [entry for entry in feed.entries if not tracker.seen_before(entry.id)]

print('Fetching %s' % URL, file=sys.stderr)
print('%s articles found; %s new' % (len(feed.entries), len(new_entries)), file=sys.stderr)

for entry in new_entries:
    emailer.send_email(FROM,
                       TO,
                       html_to_text(entry.title),
                       '%s\n\n%s' % (
                           entry.link,
                           html_to_text(entry.summary)))
    tracker.mark_seen(entry.id)
