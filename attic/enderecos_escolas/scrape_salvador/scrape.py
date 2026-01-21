#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import re
from random import randint
import sys
from urllib.parse import urlencode, quote_plus
from time import sleep

user_agent_desktop = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '\
'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '\
'Safari/537.36'

user_agent_safari = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'
headers = { 'User-Agent': user_agent_safari}
url = "https://webgen.procergs.com.br/cgi-bin/webgen2.cgi"


def get_contact(url):
    #print('get_contact',url,file=sys.stderr)
    resp = requests.get(url, headers=headers)  # Send request
    code = resp.status_code  # HTTP response code
    if code == 200:
        #soup = BeautifulSoup(resp.text, features="lxml")
        soup = BeautifulSoup(resp.text, features="html.parser")
        #print(soup.prettify())
    else:
        print(f'Failed: {code}',file=sys.stderr)

    #print(resp.text)
    escola = soup.find(id="page-single-escola")
    email = ""
    name = escola.find("h1").text
    paragraphs = escola.findAll("p")
    for p in paragraphs:
        if p.text.find("E-mail:") >= 0:
            email = p.text[8:].strip()
            break
    return name,email

    
    #url = soup.find(id="page-single-escola").find("a")['href']
 
    # resp = requests.get(url, headers=headers)
    # code = resp.status_code 
    # if code == 200:
    #     soup = BeautifulSoup(resp.text, features="lxml")
    #     html = soup.body.text
    #     email = extract_email(html)
    # else:
    #     email = None
    #     print(f'Failed: {code}',file=sys.stderr)

def extract_email(html):
    pattern = re.compile(r'([\w\.-]+@[\w\.-]+(\.[\w]+)+)')
    try:
        email = re.search(pattern,html).groups(0)[0]
    except:
        email = None
    return email

def build_search_url(name):
    #payload = {'client':'safari', 'rls':'en', 'ie': 'UTF-8', 'oe': 'UTF-8', 'q': name}
    payload = {'client':'safari', 'rls':'en', 'q': name}
    result = urlencode(payload, quote_via=quote_plus)+r'&ie=UTF-8&oe=UTF-8'
    return result
    
name = 'name'
url = "https://www.google.com/search?client=safari&rls=en&q=Col%C3%A9gio+Adventista+de+Porto+Velho&ie=UTF-8&oe=UTF-8"

filename = sys.argv[1]
fromline = int(sys.argv[2])

contacts = []
with open(filename,"r") as fschools:
    line = fschools.readline()
    lineno = 0
    while (line):
        if lineno < fromline:
            line = fschools.readline()
            lineno += 1
            continue
        try:
            search_url = line.strip()
            name,email = get_contact(search_url)
            print(name,email,sep=",")            
        except:
            print('failed',file=sys.stderr)
        
        line = fschools.readline()
        lineno += 1
        sys.stdout.flush()
        sys.stderr.flush()
        sleeptime = 10/randint(10,20)
        print(sleeptime,file=sys.stderr)
        sleep(sleeptime)


#contact = get_contact(url)
#print(extract_email(page))
