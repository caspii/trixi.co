import logging
from urllib import urlencode

import httplib2

MAILGUN_API_KEY = 'key-4b87291653134a800f45522ab1679d39'
MAILGUN_DOMAIN_NAME = 'mg.casparwre.de'
REQUEST_URL = 'https://api.mailgun.net/v3/{0}/messages'.format(MAILGUN_DOMAIN_NAME)
SUBJECT = "Project created: %s"
BODY_TEXT = "Click here to see it: https://trixi.co/project/%s"


def project_created(title, id):
    http = httplib2.Http()
    http.add_credentials('api', MAILGUN_API_KEY)

    data = {
        'from': 'Trixi <no-reply@trixi.co>',
        'to': 'Admin <caspar.wrede@gmail.com>',
        'subject': SUBJECT % title,
        'text': BODY_TEXT % id
    }
    resp, content = http.request(
        REQUEST_URL, 'POST', urlencode(data),
        headers={"Content-Type": "application/x-www-form-urlencoded"})

    if resp.status != 200:
        logging.error(
            'Mailgun API error: {} {}'.format(resp.status, content))
