'''
A script to scan a given url and links inside of that to scrap all the email ids'
'''

from bs4 import BeautifulSoup
from colorama import init as coloroma_init
from colorama import Fore, Style
import requests
import requests.exceptions
import urllib.parse
from urllib3.exceptions import LocationParseError
from collections import deque
import re

coloroma_init()


def scan_and_get_mails():
    url_to_scan = input('[+] Enter the URL to scan: ')

    if not url_to_scan.startswith('http'):
        print(
            f'{Fore.RED}[x] Please mention the full url (you have to mention wether the site follows an http or https protocol, eg:- http://example.com){Style.RESET_ALL}'
            )
        try_again_response = input('Do you want to try again? [Y/n]').lower()
        if try_again_response == 'y':
            scan_and_get_mails()
        else:
            exit()
            
    urls = deque([url_to_scan])

    scrapped_urls = []
    emails = []

    count = 0

    try:
        while True:
            count += 1
            if count == 50 or len(urls) == 0:
                break
            url = urls.popleft()
            scrapped_urls.append(url)
            
            #split the url
            parts = urllib.parse.urlsplit(url)
            base_url = '{scheme}://{netloc}'.format(scheme=parts.scheme, netloc=parts.netloc)

            path = url[:url.rfind('/')+1] if '/' in parts.path else url

            print(f'{Fore.BLUE} [{count}] Processing ----> {Style.RESET_ALL} {Fore.GREEN} {url} {Style.RESET_ALL}')
            try:
                response = requests.get(url)
            except (
                requests.exceptions.MissingSchema, 
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                LocationParseError):
                print(f'{Fore.RED} [{count}] Processing failed ----> {url} {Style.RESET_ALL}')
                continue

            #search the entire response text with regex validator for valid email addresses and save them
            found_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I)
            for mail in found_emails:
                emails.append(mail)
        
            soup = BeautifulSoup(response.text, features='lxml')

            for anchor in soup.find_all('a'):
                link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link
                if not link in urls and not link in scrapped_urls:
                    urls.append(link)
    except KeyboardInterrupt:
        print(f'{Fore.RED} [-] Keyboard interruption...closing process..! {Style.RESET_ALL}')

    print(f'\n {Fore.GREEN} Captured EMAILS: {Style.RESET_ALL} \n')
    for mail in emails:
        print(f'{mail}\n')


scan_and_get_mails()