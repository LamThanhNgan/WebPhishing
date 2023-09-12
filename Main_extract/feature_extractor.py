#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 13:23:31 2020

@author: hannousse
"""
import time
import os
import uuid
import sys
from . import content_features as ctnfe 
# import content_features as ctnfe
from . import url_features as urlfe
from . import external_features as trdfe

from . import ContentFeatures_new as ctnfe_new
from . import HostFeatures as htfe
from . import LexicalFeatures as lxfe
from webdriver_manager.chrome import ChromeDriverManager


from selenium import webdriver
from selenium.webdriver.chrome.options import Options



# import ml_models as models
import pandas as pd 
import urllib.parse
import tldextract
import requests
import json
import csv
import os
import re


# from pandas2arff import pandas2arff
from urllib.parse import urlparse
from bs4 import BeautifulSoup

key = 'gks80wkockcokoo444sok4480wgk0g480ko84kwg '

import signal


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--start-fullscreen")
chrome_options.add_argument("--window-size=1920,1040")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.set_window_size(1920,1080 )
dir = os.getcwd()
base_dir = dir + r'\Main_extract'
# cache_file_dir = base_dir + r'\data\cache.csv'

RESULTS_FILE_DIR = base_dir + r'\results\results_data_final.csv'
# data_file_dir = base_dir + r'\data\data_final.csv'


# result variables
RESULTS = {}
SUBMITED_URL = ""
PAGE_HTML = ""
FOLDER_RESULT_NAME = ""


def __print_exception__(e):
    exception_type, _, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno

    print("Exception type: ", exception_type)
    print("File name: ", filename)
    print("Line number: ", line_number)
    print("e = ", e)


def take_screenshot():
    print("=================SCREENSHOT TAKING================\n")
    global SUBMITED_URL
    global PAGE_HTML
    global FOLDER_RESULT_NAME
    url = SUBMITED_URL
    s = time.time()
    hostname, _,_ = get_domain(url)
    
    try:
        FOLDER_RESULT_NAME = base_dir + r'\\results\\' + hostname
        print("...." ,FOLDER_RESULT_NAME)
        os.mkdir(FOLDER_RESULT_NAME)
    except FileExistsError:
        __print_exception__(e)

   
    rawText = getRawHTML(content= PAGE_HTML.content)

    try:
        with open(FOLDER_RESULT_NAME + "/html.txt", "w", encoding='utf-8') as f:
            print("HTML source is saved to: " + FOLDER_RESULT_NAME)
            f.write(str(rawText))

        with open(FOLDER_RESULT_NAME + "/info.txt", "w") as f:
            f.write(url)
            
        driver.get(url)
        time.sleep(1)
        driver.save_screenshot(FOLDER_RESULT_NAME + "/shot.png")
    except Exception as e:
        removeFolder(FOLDER_RESULT_NAME)
        print("Failed to save screenshot. \n")
        __print_exception__(e)
        return False
    end = time.time()
    print("----Screenshot time ---- \n", end - s)
    return FOLDER_RESULT_NAME

    

class TimedOutExc(Exception):
    pass

# def get_all_urls_from_wayback():
#     url = SUBMITED_URL
#     base_url = 'https://web.archive.org/cdx/search/cdx?url={}/*&output=json&limit=100000&fl=original&collapse=urlkey'
#     # base_url = 'https://web.archive.org/cdx/search?url={}&matchType=prefix&collapse=urlkey&output=json&fl=original'
#     _url = base_url.format(url)
#     response = requests.get(_url)
    
#     data = response.json()

#     urls = [item[0] for item in data[1:]]
#     return urls

def deadline(timeout, *args):
    def decorate(f):
        def handler(signum, frame):
            raise TimedOutExc()

        def new_f(*args):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            return f(*args)
            signal.alarm(0)

        new_f.__name__ = f.__name__
        return new_f
    return decorate

# @deadline(5)
def is_URL_accessible(url):
    parsed = urlparse(url)
    url = parsed.scheme+'://'+parsed.netloc
    page = None
    
    try:
        page = requests.get(url, timeout=1000)   
        print("Page: ", page.status_code)
    except:
        parsed = urlparse(url)
        url = parsed.scheme+'://'+parsed.netloc
        if not parsed.netloc.startswith('www'):
            url = parsed.scheme+'://www.'+parsed.netloc
            try:
                page = requests.get(url, timeout=1000)
                print("Page: ", page.status_code)
            except:
                page = None
                pass
        # if not parsed.netloc.startswith('www'):
        #     url = parsed.scheme+'://www.'+parsed.netloc
        #     #iurl = iurl.replace('https://', 'https://www.')
        #     try:
        #         page = requests.get(url)
        #     except:        
        #         # url = 'http://'+parsed.netloc
        #         # iurl = iurl.replace('https://', 'http://')
        #         # try:
        #         #     page = requests.get(url) 
        #         # except:
        #         #     if not parsed.netloc.startswith('www'):
        #         #         url = parsed.scheme+'://www.'+parsed.netloc
        #         #         iurl = iurl.replace('http://', 'http://www.')
        #         #         try:
        #         #             page = requests.get(url)
        #         #         except:
        #         #             pass
        #         pass 
    # if page and page.content not in ["b''", "b' '"]:
    print("URL in acceptable :", url)
    if page == None or page.status_code>400:
        print("Cannot get content from this URL.")
        return False, url, page
    return True, url, page
    # else:
    #     return False, None, None

def get_domain(url):
    o = urllib.parse.urlsplit(url)
    return o.hostname, tldextract.extract(url).domain, o.path


def getPageContent(url):
    parsed = urlparse(url)
    url = parsed.scheme+'://'+parsed.netloc
    try:
        page = requests.get(url)
    except:
        if not parsed.netloc.startswith('www'):
            url = parsed.scheme+'://www.'+parsed.netloc
            page = requests.get(url)
    if page.status_code != 200:
        return None, None
    else:    
        return url, page.content
 

    
#################################################################################################################################
#              Data Extraction Process
#################################################################################################################################

def getRawHTML(content):
    soup = BeautifulSoup(content, 'html.parser', from_encoding='iso-8859-1')
    return soup

def extract_data_from_URL(hostname, content, domain, Href, Link, Anchor, Media, Metas, Form, CSS, Favicon, IFrame, Title, Text):
    #print("OK")
    Null_format = ["", "#", "#nothing", "#doesnotexist", "#null", "#void", "#whatever",
               "#content", "javascript::void(0)", "javascript::void(0);", "javascript::;", "javascript"]

    soup = BeautifulSoup(content, 'html.parser', from_encoding='iso-8859-1')
    
    # collect all external and internal hrefs from url
    try:
        for href in soup.find_all('a', href=True):
            dots = [x.start(0) for x in re.finditer('\.', href['href'])]
            if hostname in href['href'] or domain in href['href'] or len(dots) == 1 or not href['href'].startswith('http'):
                if "#" in href['href'] or "javascript" in href['href'].lower() or "mailto" in href['href'].lower():
                    Anchor['unsafe'].append(href['href']) 
                if not href['href'].startswith('http'):
                    if not href['href'].startswith('/'):
                        Href['internals'].append(hostname+'/'+href['href']) 
                    elif href['href'] in Null_format:
                        Href['null'].append(href['href'])  
                    else:
                        Href['internals'].append(hostname+href['href'])   
            else:
                Href['externals'].append(href['href'])
                Anchor['safe'].append(href['href'])
        

        # # collect all media src tags
        for img in soup.find_all('img', src=True):
            dots = [x.start(0) for x in re.finditer('\.', img['src'])]
            if hostname in img['src'] or domain in img['src'] or len(dots) == 1 or not img['src'].startswith('http'):
                if not img['src'].startswith('http'):
                    if not img['src'].startswith('/'):
                        Media['internals'].append(hostname+'/'+img['src']) 
                    elif img['src'] in Null_format:
                        Media['null'].append(img['src'])  
                    else:
                        Media['internals'].append(hostname+img['src'])   
            else:
                Media['externals'].append(img['src'])  
        
        for audio in soup.find_all('audio', src=True):
            dots = [x.start(0) for x in re.finditer('\.', audio['src'])]
            if hostname in audio['src'] or domain in audio['src'] or len(dots) == 1 or not audio['src'].startswith('http'):
                if not audio['src'].startswith('http'):
                    if not audio['src'].startswith('/'):
                        Media['internals'].append(hostname+'/'+audio['src']) 
                    elif audio['src'] in Null_format:
                        Media['null'].append(audio['src'])  
                    else:
                        Media['internals'].append(hostname+audio['src'])   
            else:
                Media['externals'].append(audio['src'])
                
        for embed in soup.find_all('embed', src=True):
            dots = [x.start(0) for x in re.finditer('\.', embed['src'])]
            if hostname in embed['src'] or domain in embed['src'] or len(dots) == 1 or not embed['src'].startswith('http'):
                if not embed['src'].startswith('http'):
                    if not embed['src'].startswith('/'):
                        Media['internals'].append(hostname+'/'+embed['src']) 
                    elif embed['src'] in Null_format:
                        Media['null'].append(embed['src'])  
                    else:
                        Media['internals'].append(hostname+embed['src'])   
            else:
                Media['externals'].append(embed['src'])
            
        for i_frame in soup.find_all('iframe', src=True):
            dots = [x.start(0) for x in re.finditer('\.', i_frame['src'])]
            if hostname in i_frame['src'] or domain in i_frame['src'] or len(dots) == 1 or not i_frame['src'].startswith('http'):
                if not i_frame['src'].startswith('http'):
                    if not i_frame['src'].startswith('/'):
                        Media['internals'].append(hostname+'/'+i_frame['src']) 
                    elif i_frame['src'] in Null_format:
                        Media['null'].append(i_frame['src'])  
                    else:
                        Media['internals'].append(hostname+i_frame['src'])   
            else: 
                Media['externals'].append(i_frame['src'])
            
        
        # # collect all link tags
        
        for url_link in soup.find_all('link',href=True):
            href = url_link['href']
            dots = [x.start(0) for x in re.finditer('\.', href)]
            
            if (hostname in href) or (domain in href) or (len(dots) == 1) or not href.startswith('http'):
                
                if not href.startswith('http'):
                    if not href.startswith('/'):
                        Link['internals'].append(hostname+'/'+href) 
                    elif href in Null_format:
                        Link['null'].append(href)  
                    else:
                        Link['internals'].append(hostname+href)   
            else:
                Link['externals'].append(href)
    

        for script in soup.find_all('script', src=True):
            dots = [x.start(0) for x in re.finditer('\.', script['src'])]
            if hostname in script['src'] or domain in script['src'] or len(dots) == 1 or not script['src'].startswith('http'):
                if not script['src'].startswith('http'):
                    if not script['src'].startswith('/'):
                        Link['internals'].append(hostname+'/'+script['src']) 
                    elif script['src'] in Null_format:
                        Link['null'].append(script['src'])  
                    else:
                        Link['internals'].append(hostname+script['src'])   
            else:
                Link['externals'].append(script['src'])
           
        
        # collect all css
        for url_link in soup.find_all('link', rel='stylesheet'):
            dots = [x.start(0) for x in re.finditer('\.', url_link['href'])]
            if hostname in url_link['href'] or domain in url_link['href'] or len(dots) == 1 or not url_link['href'].startswith('http'):
                if not url_link['href'].startswith('http'):
                    if not url_link['href'].startswith('/'):
                        CSS['internals'].append(hostname+'/'+url_link['href']) 
                    elif url_link['href'] in Null_format:
                        CSS['null'].append(url_link['href'])  
                    else:
                        CSS['internals'].append(hostname+url_link['href'])   
            else:
                CSS['externals'].append(url_link['href'])
        
        for style in soup.find_all('style', type='text/css'):
            try: 
                start = str(style[0]).index('@import url(')
                end = str(style[0]).index(')')
                css = str(style[0])[start+12:end]
                dots = [x.start(0) for x in re.finditer('\.', css)]
                if hostname in css or domain in css or len(dots) == 1 or not css.startswith('http'):
                    if not css.startswith('http'):
                        if not css.startswith('/'):
                            CSS['internals'].append(hostname+'/'+css) 
                        elif css in Null_format:
                            CSS['null'].append(css)  
                        else:
                            CSS['internals'].append(hostname+css)   
                else: 
                    CSS['externals'].append(css)
            except:
                continue
        
        # collect all form actions


        for form in soup.findAll('form', action=True):
            dots = [x.start(0) for x in re.finditer('\.', form['action'])]
            if hostname in form['action'] or domain in form['action'] or len(dots) == 1 or not form['action'].startswith('http'):
                if not form['action'].startswith('http'):
                    if not form['action'].startswith('/'):
                        Form['internals'].append(hostname+'/'+form['action']) 
                    elif form['action'] in Null_format or form['action'] == 'about:blank':
                        Form['null'].append(form['action'])  
                    else:
                        Form['internals'].append(hostname+form['action'])   
            else:
                Form['externals'].append(form['action'])
                
        
        # collect all link tags
        for head in soup.find_all('head'):
            for head.link in soup.find_all('link', href=True):
                dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
                if hostname in head.link['href'] or len(dots) == 1 or domain in head.link['href'] or not head.link['href'].startswith('http'):
                    if not head.link['href'].startswith('http'):
                        if not head.link['href'].startswith('/'):
                            Favicon['internals'].append(hostname+'/'+head.link['href']) 
                        elif head.link['href'] in Null_format:
                            Favicon['null'].append(head.link['href'])  
                        else:
                            Favicon['internals'].append(hostname+head.link['href'])   
                else:
                    Favicon['externals'].append(head.link['href'])
                    
            for head.link in soup.findAll('link', {'href': True, 'rel':True}):
                isicon = False
                if isinstance(head.link['rel'], list):
                    for e_rel in head.link['rel']:
                        if (e_rel.endswith('icon')):
                            isicon = True
                else:
                    if (head.link['rel'].endswith('icon')):
                        isicon = True
        
                if isicon:
                    dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
                    if hostname in head.link['href'] or len(dots) == 1 or domain in head.link['href'] or not head.link['href'].startswith('http'):
                        if not head.link['href'].startswith('http'):
                            if not head.link['href'].startswith('/'):
                                Favicon['internals'].append(hostname+'/'+head.link['href']) 
                            elif head.link['href'] in Null_format:
                                Favicon['null'].append(head.link['href'])  
                            else:
                                Favicon['internals'].append(hostname+head.link['href'])   
                    else:
                        Favicon['externals'].append(head.link['href'])
        
                        
        # collect i_frame
        for i_frame in soup.find_all('iframe', width=True, height=True, frameborder=True):
            if i_frame['width'] == "0" and i_frame['height'] == "0" and i_frame['frameborder'] == "0":
                IFrame['invisible'].append(i_frame)
            else:
                IFrame['visible'].append(i_frame)
        for i_frame in soup.find_all('iframe', width=True, height=True, border=True):
            if i_frame['width'] == "0" and i_frame['height'] == "0" and i_frame['border'] == "0":
                IFrame['invisible'].append(i_frame)
            else:
                IFrame['visible'].append(i_frame)
        for i_frame in soup.find_all('iframe', width=True, height=True, style=True):
            if i_frame['width'] == "0" and i_frame['height'] == "0" and i_frame['style'] == "border:none;":
                IFrame['invisible'].append(i_frame)
            else:
                IFrame['visible'].append(i_frame)
        

        
        metas = soup.find_all('meta') #Get Meta Description

        for meta in metas:
            if 'name' in meta.attrs:
                Metas.update({meta.attrs['name'].capitalize():meta.attrs['content']})
    except Exception as e:
        __print_exception__(e)
   
    # get page title
    try:
        Title = soup.title.string
    except:
        pass
    
    # get content text
    Text = soup.get_text()
    
    return Href, Link, Anchor, Media,Metas, Form, CSS, Favicon, IFrame, Title, Text, soup


#################################################################################################################################
#              Calculate features from extracted data
#################################################################################################################################


def extract_features( ):
    print("=================EXTRACT FEATURES================\n")
    global SUBMITED_URL
    global PAGE_HTML
    page = PAGE_HTML
    
    def words_raw_extraction(domain, subdomain, path):
        w_domain = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", domain.lower())
        w_subdomain = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", subdomain.lower())   
        w_path = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", path.lower())
        raw_words = w_domain + w_path + w_subdomain
        w_host = w_domain + w_subdomain
        raw_words = list(filter(None,raw_words))
        return raw_words, list(filter(None,w_host)), list(filter(None,w_path))

    
    Href = {'internals':[], 'externals':[], 'null':[]}
    Link = {'internals':[], 'externals':[], 'null':[]}
    Anchor = {'safe':[], 'unsafe':[], 'null':[]}
    Media = {'internals':[], 'externals':[], 'null':[]}
    Form = {'internals':[], 'externals':[], 'null':[]}
    CSS = {'internals':[], 'externals':[], 'null':[]}
    Favicon = {'internals':[], 'externals':[], 'null':[]}
    IFrame = {'visible':[], 'invisible':[], 'null':[]}
    Metas = {}
    Title =''
    Text= ''

    content = page.content
    hostname, domain, path = get_domain(SUBMITED_URL)
    extracted_domain = tldextract.extract(SUBMITED_URL)
    domain = extracted_domain.domain+'.'+extracted_domain.suffix
    subdomain = extracted_domain.subdomain
    tmp = SUBMITED_URL[SUBMITED_URL.find(extracted_domain.suffix):len(SUBMITED_URL)]
    pth = tmp.partition("/")
    path = pth[1] + pth[2]
    words_raw, words_raw_host, words_raw_path= words_raw_extraction(extracted_domain.domain, subdomain, pth[2])
    tld = extracted_domain.suffix
    parsed = urlparse(SUBMITED_URL)
    scheme = parsed.scheme
    
    
    Href, Link, Anchor, Media,Metas, Form, CSS, Favicon, IFrame, Title, Text , rawText= extract_data_from_URL(hostname, content, domain, Href, Link, Anchor, Media, Metas, Form, CSS, Favicon, IFrame, Title, Text)
    header = json.dumps(dict(page.headers))
    header = json.loads(header)
    h = ""
    for k, value in header.items():
        h += k + ': ' + value + '\n'
    # print(h)
    
    
    
    try: 
        row = {
        # 'length_url': urlfe.url_length(url),
        'length_hostname': urlfe.url_length(hostname),
        'ip': urlfe.having_ip_address(SUBMITED_URL),
        'nb_dots':urlfe.count_dots(SUBMITED_URL),
        'nb_hyphens': urlfe.count_hyphens(SUBMITED_URL),
        # 'nb_at', # urlfe.count_at(url),
        # 'nb_qm', # urlfe.count_exclamation(url),
        'nb_and': urlfe.count_and(SUBMITED_URL),
        # 'nb_or': urlfe.count_or(url),
        'nb_eq': urlfe.count_equal(SUBMITED_URL),
        # 'nb_underscore': # urlfe.count_underscore(url),
        # 'nb_tilde':  # urlfe.count_tilde(url),
        # 'nb_percent': # urlfe.count_percentage(url),
        'nb_slash': urlfe.count_slash(SUBMITED_URL),
        # 'nb_star': # urlfe.count_star(url),
        # 'nb_colon': # urlfe.count_colon(url),
        # 'nb_comma': # urlfe.count_comma(url),
        # 'nb_semicolumn',  # urlfe.count_semicolumn(url),
        # 'nb_dollar', # urlfe.count_dollar(url),
        # 'nb_space', # urlfe.count_space(url),
        # 'nb_www', # urlfe.check_www(words_raw),
        # 'nb_com', # urlfe.check_com(words_raw),
        # 'nb_dslash',  # urlfe.count_double_slash(url),
        'http_in_path': urlfe.count_http_token(path),
        'https_token': urlfe.https_token(scheme),
        # 'ratio_digits_url', # urlfe.ratio_digits(url),
        # 'ratio_digits_host', # urlfe.ratio_digits(hostname),
        # 'punycode', # urlfe.punycode(url),
        'port_in_url': urlfe.port(SUBMITED_URL),
        # 'tld_in_path', # urlfe.tld_in_path(tld, path),
        # 'tld_in_subdomain', # urlfe.tld_in_subdomain(tld, subdomain),
        # 'abnormal_subdomain', # urlfe.abnormal_subdomain(url),
        'nb_subdomains': urlfe.count_subdomain(SUBMITED_URL),
        # 'prefix_suffix', #  urlfe.prefix_suffix(url),
        # 'random_domain', #    urlfe.random_domain(domain),
        'shortening_service': urlfe.shortening_service(SUBMITED_URL),
        # 'path_extension', # urlfe.path_extension(path),
        
        # 'nb_redirection', # urlfe.count_redirection(page),
        # 'nb_external_redirection', # urlfe.count_external_redirection(page, domain),
        'length_words_raw': urlfe.length_word_raw(words_raw),
        # 'char_repeat', # urlfe.char_repeat(words_raw),
        'shortest_words_raw': urlfe.shortest_word_length(words_raw),
        'shortest_word_host': urlfe.shortest_word_length(words_raw_host),
        'shortest_word_path': urlfe.shortest_word_length(words_raw_path),
        'longest_words_raw': urlfe.longest_word_length(words_raw),
        'longest_word_host': urlfe.longest_word_length(words_raw_host),
        'longest_word_path': urlfe.longest_word_length(words_raw_path),
        'avg_words_raw': urlfe.average_word_length(words_raw),
        # 'avg_word_host', # urlfe.average_word_length(words_raw_host),
        'avg_word_path': urlfe.average_word_length(words_raw_path),
        # 'phish_hints',  # urlfe.phish_hints(url),  
        'domain_in_brand': urlfe.domain_in_brand(extracted_domain.domain),
        # 'brand_in_subdomain', # urlfe.brand_in_path(extracted_domain.domain,subdomain),
        # 'brand_in_path', # urlfe.brand_in_path(extracted_domain.domain,path),
        'suspecious_tld': urlfe.suspecious_tld(tld),
        'statistical_report': urlfe.statistical_report(SUBMITED_URL, domain),
        
        #    'nb_hyperlinks', # ctnfe.nb_hyperlinks(content),
        #    'ratio_intHyperlinks',  #    ctnfe.internal_hyperlinks(Href, Link, Media, Form, CSS, Favicon),
        #    'ratio_extHyperlinks', #    ctnfe.external_hyperlinks(Href, Link, Media, Form, CSS, Favicon),
        #    'ratio_nullHyperlinks', #    ctnfe.null_hyperlinks(hostname, Href, Link, Media, Form, CSS, Favicon),
        #    'nb_extCSS', #   ctnfe.external_css(CSS),
        #    'ratio_intRedirection', #      ctnfe.internal_redirection(Href, Link, Media, Form, CSS, Favicon)
        #    'ratio_extRedirection',  #      ctnfe.external_redirection(Href, Link, Media, Form, CSS, Favicon),
        #    'ratio_intErrors', #      ctnfe.internal_errors(Href, Link, Media, Form, CSS, Favicon),
        #    'ratio_extErrors', #      ctnfe.external_errors(Href, Link, Media, Form, CSS, Favicon),
            # 'login_form',  # ctnfe.login_form(Form),
            'external_favicon': ctnfe.external_favicon(Favicon),
            'links_in_tags': ctnfe.links_in_tags(Link),
        #    'submit_email', # ctnfe.submitting_to_email(Form),
            # 'ratio_intMedia', # ctnfe.internal_media(Media),
            'ratio_extMedia': ctnfe.external_media(Media),
            'sfh': ctnfe.sfh(hostname,Form),
            # 'iframe', # ctnfe.iframe(IFrame),
            'popup_window': ctnfe.popup_window(Text),
            # 'safe_anchor', # ctnfe.safe_anchor(Anchor),
            # 'onmouseover', # ctnfe.onmouseover(Text),
            # 'right_clic', # ctnfe.right_clic(Text),
            # 'empty_title', # ctnfe.empty_title(Title),
            # 'domain_in_title', # ctnfe.domain_in_title(extracted_domain.domain, Title),
            # 'domain_with_copyright', # ctnfe.domain_with_copyright(extracted_domain.domain, Text),
        
        # 'phish_hints', 
        'whois_registered_domain': trdfe.whois_registered_domain(domain), 
        'domain_registration_length': trdfe.domain_registration_length(domain),
        # 'domain_age', # trdfe.domain_age(domain),
        # 'web_traffic', # trdfe.web_traffic(url),
        # 'dns_record', # trdfe.dns_record(domain),
        # 'google_index',# trdfe.google_index(url), 
        'nameServerwhois': trdfe.nameServerwhois(domain),
        'page_rank': trdfe.page_rank(key,domain),
        'HTMLinfo': trdfe.HTMLinfo(Metas),
        'status_code': page.status_code,
        'header': h, 
        # 'domain_in_brand',
        # 'brand_in_path',
        # 'suspecious_tld',
        # 'statistical_report'
    }
        return row
    except:
        return None










#################################################################################################################################
#             Intialization
#################################################################################################################################



ctn_headers = [
                #    'nb_hyperlinks', 
                #    'ratio_intHyperlinks',
                #    'ratio_extHyperlinks', 
                #    'ratio_nullHyperlinks',
                #    'nb_extCSS',
                #    'ratio_intRedirection',
                #    'ratio_extRedirection',
                #    'ratio_intErrors',
                #    'ratio_extErrors',
                   # 'login_form', 
                   'external_favicon',
                   'links_in_tags',
                #    'submit_email', 
                   # 'ratio_intMedia',
                   'ratio_extMedia',
                   'sfh',
                   # 'iframe',
                   'popup_window',
                   # 'safe_anchor', 
                   # 'onmouseover',
                   # 'right_clic',
                   # 'empty_title', 
                   # 'domain_in_title',
                   # 'domain_with_copyright',
                                       
                ]

ctn_hyperlinks_headers = [
                   'nb_hyperlinks', 
                   'ratio_intHyperlinks',
                   'ratio_extHyperlinks', 
                   'ratio_nullHyperlinks',
                   'nb_extCSS',
                   'ratio_intRedirection',
                   'ratio_extRedirection',
                   'ratio_intErrors',
                   'ratio_extErrors',
                   'external_favicon',
                   'links_in_tags',
                   # 'ratio_intMedia',
                   'ratio_extMedia'
                ]

ctn_abnormalness_headers = [
                   # 'login_form', 
                #    'submit_email', 
                   'sfh',
                   # 'iframe',
                   'popup_window',
                   # 'safe_anchor', 
                   # 'onmouseover',
                   # 'right_clic',
                   # 'empty_title', 
                   # 'domain_in_title',
                   # 'domain_with_copyright'
                                       
                ]


    
url_headers = [    # 'length_url',                                  
                   'length_hostname',
                   'ip',
                   'nb_dots',
                   'nb_hyphens',
                   # 'nb_at',
                   # 'nb_qm',
                   'nb_and',
                   # 'nb_or',
                   'nb_eq',                  
                   # 'nb_underscore',
                   # 'nb_tilde',
                   # 'nb_percent',
                   'nb_slash',
                   # 'nb_star',
                   # 'nb_colon',
                   # 'nb_comma',
                   # 'nb_semicolumn',
                   # 'nb_dollar',
                   # 'nb_space',
                   # 'nb_www',
                   # 'nb_com',
                   # 'nb_dslash',
                   'http_in_path',
                   'https_token',
                   # 'ratio_digits_url',
                   # 'ratio_digits_host',
                   # 'punycode',
                   'port_in_url',
                   # 'tld_in_path',
                   # 'tld_in_subdomain',
                   # 'abnormal_subdomain',
                   'nb_subdomains',
                   # 'prefix_suffix',
                   # 'random_domain',
                   'shortening_service',
                   # 'path_extension',
                   
                   # 'nb_redirection',
                   # 'nb_external_redirection',
                   'length_words_raw',
                   # 'char_repeat',
                   'shortest_words_raw',
                   'shortest_word_host',
                   'shortest_word_path',
                   'longest_words_raw',
                   'longest_word_host',
                   'longest_word_path',
                   'avg_words_raw',
                   # 'avg_word_host',
                   'avg_word_path',
                   # 'phish_hints',
                   'domain_in_brand',
                   # 'brand_in_subdomain',
                   # 'brand_in_path',
                   'suspecious_tld',
                   'statistical_report'
                ]





url_stat_headers = [    
                     # 'length_url',                                  
                   'length_hostname',
                   'nb_dots',
                   'nb_hyphens',
                   # 'nb_at',
                   # 'nb_qm',
                   'nb_and',
                   # 'nb_or',
                   'nb_eq',                  
                   # 'nb_underscore',
                   # 'nb_tilde',
                   # 'nb_percent',
                   'nb_slash',
                   # 'nb_star',
                   # 'nb_colon',
                   # 'nb_comma',
                   # 'nb_semicolumn',
                   # 'nb_dollar',
                   # 'nb_space',
                   # 'nb_www',
                   # 'nb_com',
                   # 'nb_dslash',
                   'http_in_path',
                   # 'ratio_digits_url',
                   # 'ratio_digits_host',
                   'nb_subdomains',
                   
                   
                   # 'nb_redirection',
                   # 'nb_external_redirection',
                   'length_words_raw',
                   # 'char_repeat',
                   'shortest_words_raw',
                   'shortest_word_host',
                   'shortest_word_path',
                   'longest_words_raw',
                   'longest_word_host',
                   'longest_word_path',
                   'avg_words_raw',
                   # 'avg_word_host',
                   'avg_word_path',
                   # 'phish_hints',
                ]


tpt_headers = [
                   # 'phish_hints', 
                   'whois_registered_domain',
                   'domain_registration_length',
                   # 'domain_age', 
                   # 'web_traffic',
                   # 'dns_record',
                   # 'google_index',\
                   'nameServerwhois',
                   'page_rank', 
                   'HTMLinfo', 
                   'status_code',
                   'header'
                   # 'domain_in_brand',
                   # 'brand_in_path',
                   # 'suspecious_tld',
                   # 'statistical_report'
                ]

ctn_new_headers = [
                    'host', 
                    'page_entropy', 
                    'num_script_tags', 
                    # 'script_to_body_ratio', 
                    'html_length', 
                    'page_tokens', 
                    'num_sentences', 
                    'num_punctuations', 
                    'distinct_tokens', 
                    # 'capitalizations', 
                    'avg_tokens_per_sentence', 
                    'num_html_tags', 
                    # 'num_hidden_tags',
                    # 'num_iframes', 
                    # 'num_embeds', 
                    # 'num_objects', 
                    'hyperlinks', 
                    'num_whitespaces', 
                    'num_included_elemets',
                    # 'num_double_documents', 
                    'num_suspicious_elements', 
                    # 'num_eval_functions', 
                    'avg_script_length', 
                    'avg_script_entropy', 
                    # 'num_suspicious_functions'
]

hsfe_headers = [
                    # "num_subdomains", 
                    # "get_os",
                    "subdomains",
                    "get_asn",
                    "latitude", 
                    "longitude",
                    "hostnames",
                    "registration_date",
                    "expiration_date",
                    "last_updates_dates",
                    # "age",
                    "intended_life_span",
                    "life_remaining",
                    # "registrar",
                    # "reg_country",
                    "host_country",
                    "open_ports",
                    "num_open_ports",
                    "is_live",
                    "isp",
                    "connection_speed",
                    #"first_seen",
                    #"last_seen",
                    #"days_since_last_seen",
                    #"days_since_first_seen",
                    # "avg_update_days",
                    # "total_updates",
                    "ttl"
]

lxfe_headers = [
                'tld',
                'scheme',
                'url_length',
                'path_length',
                'host_length',
                # 'host_is_ip',
                'has_port_in_string',
                'num_digits',
                'parameters',
                # 'fragments',
                # 'is_encoded',
                'string_entropy',
                # 'alexa_dis_similarity',
                'subdirectories',
                'periods',
                # 'has_client',
                # 'has_login',
                # 'has_admin',
                # 'has_server',
                'num_encoded_chars'
]


l_models = ['Random Forest', 
                'SVM', #'XGBoost', 
                'Logistic Regression', 
                'Decision Tree', 
                'KNeighbors', 
                'SGD',
                'Gaussian Naive Bayes', 
                'MLP'
            ]

headers = ctn_new_headers + hsfe_headers + lxfe_headers + url_headers + ctn_headers + tpt_headers 

#################################################################################################################################
#              Generate datasets
#################################################################################################################################
import shutil
def removeFolder(folderName):
    try:
        shutil.rmtree(folderName)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

# def main_forScreenshot():
#     try:
#         os.mkdir("results")
#     except FileExistsError:
#         print("WAR: Directory already exists")
#     # read cache
#     db = pd.read_csv('data/cache.csv', on_bad_lines='skip')
#     cache = list(db['url'])
#     cache = list(set(cache))

#     dataset = pd.read_csv('data/data_final.csv')
#     lst = list(dataset['url'])
#     lst = list(set(lst))
    


#     i = 0 
#     nb = 0
    
#     nb = len(cache)
#     i = nb
    
#     for row in lst:
#         #url = 'https://'+row['domain']
#         url = row
#         print("\nTake screenshot for ", url)
        
#         if url not in cache:
#             if take_screenshot(url):
#                 state = 'OK'
#                 nb +=1 
#             else:
#                 state = 'Er'

#             with open('data/cache.csv', 'a', newline="") as cachefile :
#                 print("Saved to cache file ", url)
#                 writer = csv.writer(cachefile)
#                 writer.writerow([url])
#                 cachefile.close()
#         else:
#            state = 'Cached' 
#            i -=1
#         i+=1
#         print('[',state,']',nb,'succeded from:', i)
#         print("----------------------------------------------------------------\n")


from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from concurrent.futures import wait
from concurrent.futures import as_completed
import multiprocessing

import sys
def run_tasks_in_parallel(tasks):
    global RESULTS
    
    global FOLDER_RESULT_NAME
    start = time.time()
    with ThreadPoolExecutor(max_workers = 5) as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in as_completed(running_tasks):
            # running_task.result()
            taskres = running_task.result()
            if isinstance(taskres,str) == True:
                FOLDER_RESULT_NAME = taskres
            else:
                RESULTS.update(taskres)
    end = time.time()

    print(f"\n------------------------------------TIME-----------------------------\n: {end-start}s")
                    
    
def Extracter(urlSubmited):

    global RESULTS
    global PAGE_HTML
    global FOLDER_RESULT_NAME
    global SUBMITED_URL
    SUBMITED_URL = urlSubmited

    try:
        removeFolder(base_dir + r"\results")
        os.mkdir(base_dir + r"\results")
    except FileExistsError:
        print(e)

    print("The url submited:\n", SUBMITED_URL)

   
    nb = 0
    i = nb
        
    
    try:
        stat, _, PAGE_HTML = is_URL_accessible(SUBMITED_URL)
        if stat:
            print("\nExtract feature for ", SUBMITED_URL)
            ft_object = ctnfe_new.ContentFeatures(SUBMITED_URL)
            hfe_object = htfe.HostFeatures(SUBMITED_URL)
            lfe_object = lxfe.LexicalURLFeature(SUBMITED_URL)
            run_tasks_in_parallel([
                extract_features,
                ft_object.run,
                hfe_object.run,
                lfe_object.run,
                take_screenshot
            ])
            
            
            print("=================RESURLT================\n", RESULTS)
            print("=================LEN RESURLT================\n", len(RESULTS))
            print("=================FOLDER_RESULT_NAME:=================\n",FOLDER_RESULT_NAME)

            # u = ""
            # for url in ALL_URLS_FROM_WAYBACK[:100]:
            #     u += '{}\n'.format(url)
            # ft = ctnfe_new.ContentFeatures(url).run()
            # hfe = htfe.HostFeatures(url).run()
            # lfe = lxfe.LexicalURLFeature(url).run()
        else:
            return False, None

    except Exception as e:
        __print_exception__(e)
        return False, None

    
    if RESULTS:
        header = list(RESULTS.keys())
        print("============HEADER============\n", header)
        with open(RESULTS_FILE_DIR, 'w', newline="") as csvfile :
            writer = csv.writer(csvfile)
            writer.writerow(['url']+header)
            csvfile.close()

        url = SUBMITED_URL.split(" ")
        val = list(RESULTS.values())
        val = url + val
        
        with open(RESULTS_FILE_DIR, 'a', encoding="utf-8",newline="") as csvfile :
            writer = csv.writer(csvfile)
            writer.writerow(val)
            csvfile.close()
        state = 'OK'
        nb +=1 
    else:
        state = 'Er'
        return False, None

    i+=1
    print('[',state,']',nb,'succeded from:', i)
    print("----------------------------------------------------------------\n")

    
    # return False, None, False
    return FOLDER_RESULT_NAME, RESULTS_FILE_DIR

    


# if __name__ == '__main__':
    # generate_external_dataset(headers)
    # main_forScreenshot()
    # content features 63 
