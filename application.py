from flask import Flask
from flask import jsonify
from flask import request
from newsapi import NewsApiClient
import re
from collections import Counter, defaultdict
from operator import itemgetter

from newsapi.newsapi_exception import NewsAPIException

application = Flask(__name__, static_url_path='')
# Init
newsapi = NewsApiClient(api_key='4cf493338f8b4a8483e9a07261b22e83')

def index():
    return application.send_static_file("index.html")
application.add_url_rule('/', 'index', index)

# author, description, title, url, urlToImage, publishedAt and source with its inner keys)
def get_top_headlines():
    # read the parameter send by the frontend using GET request
    if 'src' in request.args:
        src = request.args.get('src')
        top_headlines = newsapi.get_top_headlines(sources=src, language='en', page_size=30)
        headline_count = 4
    else:
        top_headlines = newsapi.get_top_headlines(language='en', page_size=30)
        headline_count = 5
    print(top_headlines)
    valid_headlines = []
    for each in top_headlines['articles']:
        if isvalid(each):
            del each['content']
            valid_headlines.append(each)
    valid_headlines = valid_headlines[:headline_count]
    return jsonify(valid_headlines)
application.add_url_rule('/topheadlines', 'get_top_headlines', get_top_headlines)


def word_cloud():
    top_headlines = newsapi.get_top_headlines(language='en', page_size=30)
    #print(top_headlines)
    l=[]
    #p=0
    f = open("stopwords_en.txt")
    stopset = set(f.read().split("\n"))
    #print(stopset)
    for each in top_headlines['articles']:
        #print(each)
        if each['title'] != None :
            #p +=1
            line = each['title'].split()
            #print(line)
            for word in line:
                clean_word = re.sub('[^\w\-]+', '', word)
                if clean_word.casefold() not in stopset and len(clean_word) :
                    l.append(clean_word)
    c = Counter(l).most_common(30)
    #c = list(map(itemgetter(0), c))
    #print(p)
    print(c)
    ll=[]
    #d=defaultdict()
    for each in c:
        d={}
        #d = defaultdict()
        d['word']=each[0]
        d['size']=each[1]*10
        ll.append(d)
    print(ll)
    return jsonify(ll)
application.add_url_rule('/wordcloud', 'word_cloud',word_cloud)

def get_dynamic_sources():
    if 'cat' in request.args:
        cat = request.args.get('cat')
        get_sources = newsapi.get_sources(category=cat, language='en', country='us')
    else:
        get_sources = newsapi.get_sources(language='en', country='us')
    l = []
    c = 0
    for each in get_sources["sources"]:
        l.append(each)
        c += 1
        if c==10:
            break
    return jsonify(l)
application.add_url_rule('/dynamicsources', 'get_dynamic_sources', get_dynamic_sources)

def get_search_data():
    data = request.form
    print(data)
    # keyword = data['keyword']
    # from_date = data['from']
    # to_date = data['to']
    # category = data['category']
    try:
        if data['sources'] == "all":
            all_articles = newsapi.get_everything(q=data['keyword'], from_param=data['from'], to=data['to'],language='en', page_size=30,
                                                  sort_by="publishedAt")
        else:
            all_articles = newsapi.get_everything(q=data['keyword'],from_param=data['from'],to=data['to'], sources=data['sources'], language='en',page_size=30,sort_by="publishedAt")
        valid_articles = []
        article_count = 15
        for each in all_articles['articles']:
            if isvalid(each):
                del each['content']
                valid_articles.append(each)
        valid_articles = valid_articles[:article_count]
        return jsonify(valid_articles)
    except NewsAPIException as e:
        return jsonify({'message': e.get_message()})
application.add_url_rule('/searchdata', 'get_search_data', get_search_data,methods=['POST'])


def isvalid(each):
    flag=0
    if each['author'] != None and each['description'] != None and each['title'] != None and each['url'] != None and \
            each['urlToImage'] != None and each['publishedAt'] != None and each['source'] != None and \
            each['source']['id'] != None and each['source']['name'] != None :
        flag+=1
    if each['author'] != "null" and each['description'] != "null" and each['title'] != "null" and each['url'] != "null" and \
            each['urlToImage'] != "null" and each['publishedAt'] != "null" and each['source'] != "null" and \
            each['source']['id'] != "null" and each['source']['name'] != "null" :
        flag+=1
    if each['author'] != "" and each['description'] != "" and each['title'] != "" and each['url'] != "" and \
            each['urlToImage'] != "" and each['publishedAt'] != "" and each['source'] != "" and \
            each['source']['id'] != " " and each['source']['name'] != "" :
        flag+=1

    if flag==3:
        return True

    return False
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    application.debug = True
    application.run()
