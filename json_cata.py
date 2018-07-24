from pymonad import Just,Result
from functools import reduce
import pymonad as md 
import pyramda as r 
from soup import at3
import bs4

def fmap(f, data):
    if isinstance(data, list):
        return [f(x) for x in data]
    if isinstance(data, dict):
        return {k: f(v) for (k, v) in data.items()}
    # if isinstance(data,int):
    #     return int(f(data))
    return data


def cata(f, data):
    # First, we recurse inside all the values in data
    cata_on_f = lambda x: cata(f, x)
    recursed = fmap(cata_on_f, data)
    # Then, we apply f to the result
    return f(recursed)

def sum_one_level(data):
    print('data',data,type(data))
    if isinstance(data, list):
        result = reduce(lambda x,y: y+x, data)
        print('result: {}'.format(result))
        return result
        
    return data

def add2_one_level(data):
    if isinstance(data,int):
        return data+2
    return data


def add_layer_one_level(data):
    if isinstance(data,int):
        return [data]
    return data

def just_one_level(data):
    print('data',data,type(data))
    if isinstance(data, Just):
        if isinstance(data.value,list):
            result = reduce(lambda x,y: x+y, data)
            print('result: {}'.format(result))
            return result
    return data

def localize_one_level(lang, data):
    if isinstance(data, dict) and lang in data:
        return data[lang]
    return data


def localize2(lang, data):
    localize_one_level_on_lang = lambda x: localize_one_level(lang, x)
    return cata(localize_one_level_on_lang, data)


val = { "en": "This is a sentence in english", "fr": "Ceci est une phrase en français"}

tagfn = lambda fn: r.if_else(r.isinstance(bs4.element.Tag),fn,r.identity)
scalarfn = lambda fn: r.if_else(r.isinstance(list),r.identity,maybe_none_resolver)

data = cata(tagfn(me.find_all('tr')),at3)
data2 = cata(tagfn(me.find_all('td')), data)
data_texts = cata(tagfn(mn.get_text()), data2 )
data3 = cata(tagfn(mn.find('a')), data2 )
data_titles = cata(tagfn(mn.get('title')), data3 )
data_links = cata(tagfn(mn.get('href')), data3 )
#data5 = cata(tagfn(maybe_none_resolver),data4)

uw_titles = cata(lambda x: x.value if isinstance(x,md.Maybe) else x, data_titles)
uw_texts = cata(lambda x: x.value if isinstance(x, md.Maybe) else x, data_texts)
w_titles = cata(r.if_else(r.isinstance(list),r.identity,r.compose(md.First,maybe_none_resolver)), uw_titles )
w_texts = cata(r.if_else(r.isinstance(list),r.identity, maybe_none_resolver), uw_texts )

out = cata( r.if_else(lambda x: True if isinstance(x,tuple) and isinstance(x[0],md.Container) else False, r.apply(r.add),r.identity),  (w_titles,w_texts) )

out2 = cata( r.if_else(r.isinstance(md.First), lambda x: x.value.value, r.identity ), out )
out3 = cata( r.if_else(r.isinstance(md.Just), lambda x: x.value, r.identity ), out2 )