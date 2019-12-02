"""
Defines a function that fetches a random cat image and emails it to an address.
The function is intended to be run by Amazon's Lambda.
"""

import base64
import os

import boto3
import requests

def html_email(content):
    """
    Wrap the content in a valid html container.
    The content will be the immediate child of the body tag.
    """
    return """<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>An email</title></head><body>{}</body></html>""".format(content)

def email_text(message):
    """Wrap the message in the dict that describes text for the boto3 SES client."""
    return {
        'Data': message,
        'Charset': 'UTF-8'
    }

def emails(address):
    """Wraps the email address in an array or returns an empty array if no address is provided"""
    if address is None:
        return []
    return [address]

def cat_image_url():
    """Fetches the url for a random cat image"""
    resp = requests.get(
        'http://thecatapi.com/api/images/get?format=src&size=small',
        allow_redirects=False
    )
    return resp.headers['location']

def img_tag(src, alt=None):
    """Returns a string containing the html img tag"""
    components = [
        'src="{}"'.format(src)
    ]
    if alt is not None:
        components.append('alt="{}"'.format(alt))
    return '<img {}>'.format(' '.join(components))

def sendEmail(event, context): #pylint: disable=unused-argument
    """The handler function run by Amazon's Lambda"""
    data = event['body']

    source = data['source']
    assert source != None, 'The SOURCE environment variable is required.'

    to_address = data['destination']
    assert to_address != None, 'The RECIPIENT environment variable is required.'

    subject = data['subject']

    backup_text = os.environ.get('BACKUP', 'A picture of a cat!')
    reply_to_addresses = emails(os.environ.get('REPLYTO', None))

    url = cat_image_url()
    content = img_tag(url, backup_text)

    client = boto3.client('ses')
    response = client.send_email(
        Source=source,
        Destination={
            'ToAddresses': [to_address]
        },
        Message={
            'Subject': email_text(subject),
            'Body': {
                'Html': email_text(html_email(content)),
                'Text': url
            }
        },
        ReplyToAddresses=reply_to_addresses
    )
