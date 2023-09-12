from os import linesep
from math import log
from re import compile
from urllib.parse import urlparse

from socket import gethostbyname
from pyquery import PyQuery
from requests import get

from string import ascii_lowercase
from numpy import array
import sys

cache = []

#with open('FinalDataset/output/data_url_screenshot_zeroday_lexicalfeatures.json', 'r+') as ff:
#   data = [loads(i) for i in ff.readlines()]
#   seen = [i['host'] for i in data]
#   for i in seen:
#       print('Caching {}'.format(i))
#       cache.append(i)

'''Get Alexa top 50 sites'''
def __get_alexa_top_50():
    pq = PyQuery(get('https://www.alexa.com/topsites').content)
    items = pq('.site-listing .DescriptionCell p a')
    sites = [i.text().lower() for i in items.items()]
    return sites
alexa_50 = __get_alexa_top_50()


class alexa_similarity:
    def __init__(self, url):
        self.alexa50 = alexa_50
        self.url = url

    '''Remove none numeric or alphabetic characters from URL strings'''
    def clean_url(self, url):
        url = ''.join([i for i in url.lower() if i.isalpha() or i.isalpha()])
        return url

    '''Get list of common characters between two URL strings'''
    def similar_string_score(self, string1:str, string2: str):
        string1, string2 = string1.lower(), string2.lower()
        return list(set(string1) & set(string2))

    '''count the frequency occurance of common charaters in both strings'''
    def count_freq_similar(self, string1: str, string2: str):
        sims = self.similar_string_score(string1, string2)
        if len(sims) == 0:
            return 0
        sim1 = [string1.count(i) for i in sims]
        sim2 = [string2.count(i) for i in sims]
        a = sum(abs(array(sim1) - array(sim2)))
        return a

    '''Get the ascii positional index of a letter'''
    def get_pos(self, char: str):
        try:
            pos = ascii_lowercase.index(char.lower()) if char.isalpha else char
            return int(pos)
        except:
            return 0

    '''Estimate alpha numeric distribution difference'''
    def andd(self, string1: str, string2: str):
        corpus = list(map(self.clean_url, [string1, string2]))
        shorter, longer = min(corpus, key=len), max(corpus, key=len)
        diff = len(longer) - len(shorter)
        corpus[corpus.index(shorter)] = shorter + ('0' * diff)
        diffs = [abs(self.get_pos(corpus[0][i]) - self.get_pos(corpus[1][i])) for i in range(0, len(longer))]
        return sum(diffs)/len(diffs)

    '''Estimate how dis similar 2 URLs are'''
    def alexa_dis_similarity(self):
        self.url = self.clean_url(self.url)
        x = {i: self.count_freq_similar(self.url, self.clean_url(i)) for i in self.alexa50}
        x = {k: v for k, v in x.items() if v < 5}
        #print(x)
        if len(x) > 0:
            diffs = [self.andd(self.url, self.clean_url(k)) for k in list(x.keys())]
            return sum(diffs)/len(diffs)
        else:
            return 0


class LexicalURLFeature:
    def __init__(self, url):
        self.description = 'blah'
        self.url = url
        self.urlparse = urlparse(self.url)
        self.alexa = alexa_similarity(self.url)
        self.host = self.__get_ip()


    def __get_entropy(self, text):
        text = text.lower()
        probs = [text.count(c) / len(text) for c in set(text)]
        entropy = -sum([p * log(p) / log(2.0) for p in probs])
        return entropy

    def __get_ip(self):
        try:
            ip = self.urlparse.netloc if self.url_host_is_ip() else gethostbyname(self.urlparse.netloc)
            return ip
        except:
            return None

    # extract lexical features
    def url_scheme(self):
        #print(self.url)
        #print(self.urlparse)
        return self.urlparse.scheme

    def url_length(self):
        return len(self.url)

    def url_path_length(self):
        return len(self.urlparse.path)

    def url_host_length(self):
        return len(self.urlparse.netloc)

    def url_host_is_ip(self):
        host = self.urlparse.netloc
        pattern = compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        match = pattern.match(host)
        return match is not None

    def url_has_port_in_string(self):
        has_port = self.urlparse.netloc.split(':')
        return len(has_port) > 1 and has_port[-1].isdigit()

    def number_of_digits(self):
        digits = [i for i in self.url if i.isdigit()]
        return len(digits)

    def number_of_parameters(self):
        params = self.urlparse.query
        return 0 if params == '' else len(params.split('&'))

    def number_of_fragments(self):
        frags = self.urlparse.fragment
        return len(frags.split('#')) - 1 if frags == '' else 0

    def is_encoded(self):
        return '%' in self.url.lower()

    def num_encoded_char(self):
        encs = [i for i in self.url if i == '%']
        return len(encs)

    def url_string_entropy(self):
        return self.__get_entropy(self.url)

    def average_alexa_50_similarity(self):
        return self.alexa.alexa_dis_similarity()

    def number_of_subdirectories(self):
        d = self.urlparse.path.split('/')
        return len(d)

    def number_of_periods(self):
        periods = [i for i in self.url if i == '.']
        return len(periods)

    def has_client_in_string(self):
        return 'client' in self.url.lower()

    def has_admin_in_string(self):
        return 'admin' in self.url.lower()

    def has_server_in_string(self):
        return 'server' in self.url.lower()

    def has_login_in_string(self):
        return 'login' in self.url.lower()

    def get_tld(self):
        return self.urlparse.netloc.split('.')[-1].split(':')[0]

    def run(self):
        print("=================LEXICAL FEATURES================\n")
        try:
            fv = {
                  # 'host': self.host,
                   'tld': self.get_tld(),
                  'scheme': self.url_scheme(),
                  'url_length': self.url_length(),
                  'path_length': self.url_path_length(),
                  'host_length': self.url_host_length(),
                  # 'host_is_ip': self.url_host_is_ip(),
                  'has_port_in_string': self.url_has_port_in_string(),
                  'num_digits': self.number_of_digits(),
                  'parameters': self.number_of_parameters(),
                  # 'fragments': self.number_of_fragments(),
                  # 'is_encoded': self.is_encoded(),
                  'string_entropy': self.url_string_entropy(),
                  # 'alexa_dis_similarity': self.average_alexa_50_similarity(),
                  'subdirectories': self.number_of_subdirectories(),
                  'periods': self.number_of_periods(),
                  # 'has_client': self.has_client_in_string(),
                  ## 'has_login': self.has_login_in_string(),
                  # 'has_admin': self.has_admin_in_string(),
                  # 'has_server': self.has_server_in_string(),
                  'num_encoded_chars': self.num_encoded_char()
                     }
            return fv
        except Exception as e:
            exception_type, _, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno

            print("Exception type: ", exception_type)
            print("File name: ", filename)
            print("Line number: ", line_number)
            print("e = ", e)
            return {}
#ob = LexicalURLFeature("http://1337x.to/torrent/1048648/American-Sniper-2014-MD-iTALiAN-DVDSCR-X264-BST-MT/")
#ob.run()

# if __name__ == '__main__':
#     # files = os.listdir('data')
#     files = ['URL_result_alive_url2016_benign_2000.csv']
#     for file in files:
#         file = 'FinalDataset/URL/{}'.format(file)
#         with open(file, 'r+') as ff:
#             lines = [i.strip() for i in ff.readlines()][::-1]
#             for line in lines:
#                 tag = line
#                 ft = LexicalURLFeature(line).run()
#                 if ft is not None:
#                     ft['url'] = tag
#                     with open('FinalDataset/output/data_url_screenshot_benign_lexicalfeatures_2000.json', 'a') as jj:
#                         dump(ft, jj)
#                         jj.write('\n')
#                         print(ft)
#                 else:
#                     pass