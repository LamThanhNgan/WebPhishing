from urllib.parse import urlparse
from pyquery import PyQuery
from requests import get
from socket import gethostbyname
from numpy import array, log
from string import punctuation
from json import dump, loads
from re import compile

cache = []

# with open('FinalDataset/output/data_url_screenshot_benign_contentfeatures_2000.json', 'r+') as ff:
#    data = [loads(i) for i in ff.readlines()]
#    seen = [i['url'] for i in data]
#    for i in seen:
#        print('Caching {}'.format(i))
#        cache.append(i)

# def __get_valid_html_tags():
#     pq = PyQuery(get('https://htmldog.com/references/html/tags/').content)
#     items = pq('.longlist.acodeblock ul li a code')
#     print("OK\n", items)
#     tags = [i.text().lower() for i in items.items()]
#     return tags
import os, sys
def __txt_to_list(txt_object):
    list = []
    for line in txt_object:
        list.append(line.strip())
    txt_object.close()
    return list
def __get_suspicious_functions():
    txt = open(os.path.join(os.path.dirname(__file__), 'mal_script_functions.txt'), "r")
    content = []
    for line in txt:
        content.append(line.strip())
    txt.close()
    return content

# vd = __get_valid_html_tags()
sf = __get_suspicious_functions()

class ContentFeatures:
    def __init__(self, url, vd = "", sf = sf):
        self.url = url
        self.urlparse = urlparse(self.url)
        self.host = self.__get_ip()
        self.html = self.__get_html()
        self.pq = self.__get_pq()
        self.scripts = self.__get_scripts()
        self.valid_tags = ""
        self.suspicious_functions = sf

    def __get_ip(self):
        try:
            ip = self.urlparse.netloc if self.url_host_is_ip() else gethostbyname(self.urlparse.netloc)
            return ip
        except:
            return 0


    def url_host_is_ip(self):
        host = self.urlparse.netloc
        pattern = compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        match = pattern.match(host)
        return match is not None

    def __get_html(self):
        try:
            html = get(self.url)
            html = html.text if html else 0
        except:
            html = 0
        return html

    def __get_pq(self):
        try:
            pq = PyQuery(self.html) if self.html else 0
            return pq
        except:
            return 0


    def __get_scripts(self):
        scripts = self.pq('script') if self.pq else 0
        return scripts

    def __get_entropy(self, text):
        text = text.lower()
        probs = [text.count(c) / len(text) for c in set(text)]
        return -sum([p * log(p) / log(2.0) for p in probs])

    #extract content-based features
    def url_page_entropy(self):
        return self.__get_entropy(self.html)

    def number_of_script_tags(self):
        return len(self.scripts) if self.scripts else 0

    def script_to_body_ratio(self):
        if self.scripts:
            scripts = self.scripts.text()
            return len(scripts)/self.length_of_html()
        else:
            return 0

    def length_of_html(self):
        return len(self.html)

    def number_of_page_tokens(self):
        html_tokens = len(self.html.lower().split()) if self.html else 0
        return html_tokens

    def number_of_sentences(self):
        html_sentences = len(self.html.split('.')) if self.html else 0
        return html_sentences

    def number_of_punctuations(self):
        excepts = ['<', '>', '/']
        matches = [i for i in self.html if i in punctuation and i not in excepts]
        return len(matches)

    def number_of_distinct_tokens(self):
        html_tokens = [i.strip() for i in self.html.lower().split()]
        return len(set(html_tokens))

    def number_of_capitalizations(self):
        uppercases = [i for i in self.html if i.isupper()]
        return len(uppercases)

    def average_number_of_tokens_in_sentence(self):
        html_sentences = self.html.split('.')
        sen_lens = [len(i.split()) for i in html_sentences]
        return sum(sen_lens)/len(sen_lens)

    def number_of_html_tags(self):
        return len(self.pq('*')) if self.pq else 0

    def number_of_hidden_tags(self):
        hidden1, hidden2 = self.pq('.hidden'), self.pq('#hidden')
        hidden3, hidden4 = self.pq('*[visibility="none"]'), self.pq('*[display="none"]')
        hidden = hidden1 + hidden2 + hidden3 + hidden4
        return len(hidden)

    def number_iframes(self):
        iframes = self.pq('iframe') + self.pq('frame')
        return len(iframes)

    def number_objects(self):
        objects = self.pq('object')
        return len(objects)

    def number_embeds(self):
        objects = self.pq('embed')
        return len(objects)

    def number_of_hyperlinks(self):
        hyperlinks = self.pq('a')
        return len(hyperlinks)

    def number_of_whitespace(self):
        whitespaces = [i for i in self.html if i == ' ']
        return len(whitespaces)

    def number_of_included_elements(self):
        toi = self.pq('script') + self.pq('iframe') + self.pq('frame') + self.pq('embed') + self.pq('form') + self.pq('object')
        toi = [tag.attr('src') for tag in toi.items()]
        return len([i for i in toi if i])

    def number_of_suspicious_elements(self):
        all_tags = [i.tag for i in self.pq('*')]
        suspicious = [i for i in all_tags if i not in self.valid_tags]
        return len(suspicious)

    def number_of_double_documents(self):
        tags = self.pq('html') + self.pq('body') + self.pq('title')
        return len(tags) - 3

    def number_of_eval_functions(self):
        scripts = self.pq('script')
        scripts = ['eval' in script.text().lower() for script in scripts.items()]
        return sum(scripts)

    def average_script_length(self):
        scripts = self.pq('script')
        scripts = [len(script.text()) for script in scripts.items()]
        l = len(scripts)
        if l > 0:
            return sum(scripts) / l
        else:
            return 0

    def average_script_entropy(self):
        scripts = self.pq('script')
        scripts = [self.__get_entropy(script.text()) for script in scripts.items()]
        l = len(scripts)
        if l > 0:
            return sum(scripts) / l
        else:
            return 0

    def number_of_suspicious_functions(self):
        script_content = self.pq('script').text()
        susf = [1 if i in script_content else 0 for i in self.suspicious_functions]
        return sum(susf)

    def run(self):
        print("=================CONTENT FEATURES================\n")
        data = {}
        try:
            if self.html and self.pq:
                data['host'] = self.host
                data['page_entropy'] = self.url_page_entropy()
                data['num_script_tags'] = self.number_of_script_tags()
                # data['script_to_body_ratio'] = self.script_to_body_ratio()
                data['html_length'] = self.length_of_html()
                data['page_tokens'] = self.number_of_page_tokens()
                data['num_sentences'] = self.number_of_sentences()
                data['num_punctuations'] = self.number_of_punctuations()
                data['distinct_tokens'] = self.number_of_distinct_tokens()
                # data['capitalizations'] = self.number_of_capitalizations()
                data['avg_tokens_per_sentence'] = self.average_number_of_tokens_in_sentence()
                data['num_html_tags'] = self.number_of_html_tags()
                # data['num_hidden_tags'] = self.number_of_hidden_tags()
                # data['num_iframes'] = self.number_iframes()
                # data['num_embeds'] = self.number_embeds()
                
                # data['num_objects'] = self.number_objects()
                data['hyperlinks'] = self.number_of_hyperlinks()
                data['num_whitespaces'] = self.number_of_whitespace()
                data['num_included_elemets'] = self.number_of_included_elements()
                # data['num_double_documents'] = self.number_of_double_documents()
                data['num_suspicious_elements'] = self.number_of_suspicious_elements()
                # data['num_eval_functions'] = self.number_of_eval_functions()
                data['avg_script_length'] = self.average_script_length()
                data['avg_script_entropy'] = self.average_script_entropy()
                # data['num_suspicious_functions'] = self.number_of_suspicious_functions()
                cache.append(self.url)
            else:
                pass
        except Exception as e:
            exception_type, _, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno

            print("Exception type: ", exception_type)
            print("File name: ", filename)
            print("Line number: ", line_number)
            print("e = ", e)
            data = {}
        
        return data
