#!/usr/bin/python

import os
import re
import json
import time
import requests
import smtplib
import argparse
import urlparse
from copy import copy
from lxml import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(price, url, email_info):
    try:
        s = smtplib.SMTP(email_info['smtp_url'])
        s.starttls()
        s.login(email_info['user'], email_info['password'])
    except smtplib.SMTPAuthenticationError:
        print('Failed to login')
    else:
        print('Logged in! Composing message..')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Price Alert - %s' % price
        msg['From'] = email_info['user']
        msg['To'] = email_info['user']
        text = 'Jabong price is lower than benchmark set.Their price is currently %s !! URL to salepage: %s' % (
            price, url)
        part = MIMEText(text, 'plain')
        msg.attach(part)
        s.sendmail(email_info['user'], email_info['user'], msg.as_string())
        print('Message has been sent.')


def get_price(url, selector):
    page = requests.get((url+".html"), headers={
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    })
    page.raise_for_status()
    doc = html.fromstring(page.content)
    try:
         XPATH_SALE_PRICE = '//*[@id="pdp-price-info"]/span[3]/text()'
         RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
         price_string = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
         print(price_string)
         return (price_string.replace('.00', ''))
    except IndexError, TypeError:
         print('Didn\'t find the \'price\' element, trying again later...')


def get_config(config):
    with open(config, 'r') as f:
        return json.loads(f.read())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        default='%s/config.json' % os.path.dirname(
                            os.path.realpath(__file__)),
                        help='Configuration file path')
    parser.add_argument('-t', '--poll-interval', type=int, default=30,
                        help='Time in seconds between checks')
    return parser.parse_args()


def main():
    args = parse_args()
    config = get_config(args.config)
    items = config['items']

    while True and len(items):
        for item in copy(items):
            print('Checking price for %s (should be lower than %s)' % (
                item[0], item[1]))
            #print item[0]
            print (type(item[0]))
            print item[1]
            print (type(item[1]))
            item_page = urlparse.urljoin(config['base_url'], item[0])
            price = get_price(item_page, config['xpath_selector'])
            print price
            #print (type(price))
            z = int(price.replace(',', ''))
            print z
            print (type(z))
            
            if z > item[1]:
                print('Price is %s. Ignoring...' % z)
            else:
                print('Price is %s!! Trying to send email.' % z)
                send_email(price, item_page, config['email'])
                items.remove(item)
            #else:
             #   print('Price is %s. Ignoring...' % price)

        if len(items):
            print('Sleeping for %d seconds' % args.poll_interval)
            time.sleep(args.poll_interval)
        else:
            break
    print('Price alert triggered for all items, exiting.')

if __name__ == '__main__':
    main()
