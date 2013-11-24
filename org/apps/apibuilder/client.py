#!/usr/bin/env python
import urllib
import urllib2
import base64
from getpass import getpass
from zlib import decompress
import sys
try:
    import cPickle as pickle
except ImportError:
    import pickle

class DoesNotExist(Exception): pass
class MultipleReturned(Exception): pass

def http_auth(separator=':',*args):
    """
    Returns HTTP Basic Auth header (base64 encoded)
    Separator is ususally ':' for most browsers
    Args are ususallly username and raw_password (can be API key)
    """
    return 'Basic %s'%base64.b64encode(separator.join(map(str, args)))

def auth_header(username,raw_password):
    """Authorization header for HTTP requests"""
    return {'Authorization':http_auth(':', username, raw_password)}
    
def auth_env(username, raw_password):
    """Environment header for CGI/WSGI apps"""
    return {'HTTP_AUTHORIZATION':http_auth(':', username, raw_password)}

def key_header(key):
    """Authorization header for HTTP requests"""
    return {'Authorization':http_auth('$', key)}
    
def key_env(key):
    """Environment header for CGI/WSGI apps"""
    return {'HTTP_AUTHORIZATION':http_auth('$', key)}

def delete(url, *args, **kwargs):
    """Delete a resource on the given url
    
    @param url: URL path on the API server
    """
    headers = {}
    try:
        username,raw_password = args
    except:
        username,raw_password = None,None
    if username is None:
        username = raw_input('Username: ')
    if raw_password is None:
        raw_password = getpass()
    if username and raw_password:
        headers =  auth_header(username, raw_password)
    url = '%s?%s'%(url,urllib.urlencode(params))
    req = urllib2.Request(url, None, headers, method='DELETE')
    return urllib2.urlopen(req)

def commit(url, *args, **kwargs):
    """Send a commit message to the API server and return the response
    
    @param url: URL path on the API server
    """
    headers = {}
    try:
        username,raw_password = args
    except:
        username,raw_password = None,None
    if username is None:
        username = raw_input('Username: ')
    if raw_password is None:
        raw_password = getpass()
    if username and raw_password:
        headers =  auth_header(username, raw_password)
    req = urllib2.Request(url, urllib.urlencode(kwargs), headers, method='POST')
    return urllib2.urlopen(req)
    
def query(url, *args, **kwargs):
    """Retrieve the QuerySet provided in the URL and return the response
    
    @param url: URL path on the API server
    """
    try:
        headers =  auth_header(*args)
    except:
        headers = {}
    url = '%s?%s'%(url,urllib.urlencode(kwargs))
    req = urllib2.Request(url, None, headers, method='GET')
    return urllib2.urlopen(req)
    
def topython(url, *args, **kwargs):
    """Same as an api_query, but returns the native python dict
    Uses compressed pickles for transfer
    """
    kwargs['_format'] = 'pickle'
    kwargs['_compression'] = 9
    response = query(url, *args, **kwargs)
    return pickle.loads(decompress(response.read()))

class RemoteQuerySet(object):
    """Remote wrapper for api_query
    Emulates django.db.models.query.QuerySet
    Aimed at functional replacement
    TODO: Match QuerySet 1:1, make it lazier
    """
    def __init__(self, url, app, model, *args, **kwargs):
        self.base_url = url
        self.query_url = self.base_url + '%s/%s/'%(app,model)
        self.commit_url =  self.base_url + 'admin/' + self.query_url
        self.args =  args
        kwargs['_format'] = 'pickle'
        self.kwargs = kwargs
    
    def reassign(self, app, model):
        self.query_url = self.base_url + '%s/%s/'%(app,model)
        self.commit_url =  self.base_url + 'admin/' + self.query_url
    
    def count(self):
        self.kwargs['_count'] = True
        return int(query(self.query_url, *self.args, **self.kwargs).read())
    __len__ = count
    
    def distinct(self, true_or_false):
        self.kwargs['_distinct'] = int(bool(true_or_false))
        return self
    
    def extra(self, *a, **kw):
        """No WAI"""
        return self
    
    def defer(self, *fields):
        """No WAI"""
        return self
    
    def only(self, *fields):
        self.kwargs['_fields'] = ','.join(map(str, fields))
        return self
    
    def filter(self, **kwargs):
        self.kwargs.update(kwargs)
        return self
    
    def order_by(self, *args):
        self.kwargs['_order_by'] = ','.join(map(str, args))
        return self

    def iterator(self):
        return topython(self.query_url, *self.args, **self.kwargs)

    def dump(self, output_file=None, **kwargs):
        self.kwargs.update(kwargs)
        if output_file and not hasattr(output_file,'write'):
            output_file = open(output_file,'wb')
        elif output_file is None:
            output_file = sys.stdout
        output_file.write(
            query(self.query_url, *self.args, **self.kwargs).read()
        )
    
    def exclude(self, **kwargs):
        for k,v in kwargs.items():
            self.kwargs['%s__exclude'%k] = v
        return self
     
    def all(self):    return self
    
    def get(self, **kwargs):
        kwargs['_limit'] = 1
        self.filter(**kwargs)
        num = len(self)
        if num == 1:
            return self.iterator()[0]
        elif num:
            raise MultipleReturned
        raise DoesNotExist
        
    def create(self, **kwargs):
        return self.get(pk=commit(self.commit_url, *self.args, **kwargs).read())
        
    def get_or_create(self, **kwargs):
        try:
            return self.get(**kwargs), False
        except DoesNotExist:
            return self.create(**kwargs), True
            
    def delete(self, pk):
        return delete(self.commit_url + '%s/'%pk, *self.args, **self.kwargs).read()
    
    def update(self, **kwargs):
        self.kwargs.update(kwargs)
        return commit(self.commit_url, *self.args, **self.kwargs).read()

    def latest(self, field_name, **kwargs):
        kwargs.update({
            '_limit': 1,
            '_order_by': '-%s' % field_name
        })
        return self.get(**kwargs)
    
    def select_related(self, *fields, **kwargs):
        kwargs['_relations'] = ','.join(fields)
        self.kwargs.update(kwargs)
        return self
    
    @property
    def ordered(self):
        return '_order_by' in self.kwargs
    
    def reverse(self):
        ordering = self.kwargs.get('_order_by','').split(',')
        ordering.reverse()
        self.kwargs['_order_by'] = ','.join(ordering)
        return self        
    
    def in_bulk(self, id_list):
        if not id_list:
            return {}
        if isinstance(id_list, list) or isinstance(id_list, tuple):
            id_list = ','.join(map(str,id_list))
        self.filter(pk__in=id_list)
        return dict(((obj['pk'], obj['fields']) for obj in self.iterator()))

    def pprint(self):
        from pprint import pprint
        pprint(self.iterator())
        
def rpc_query(url, func, *a, **kw):
    import xmlrpclib
    return getattr(xmlrpclib.ServerProxy(url), func)(*a, **kw)

if __name__ == '__main__':
    from random import randint
    i = 2
    print 5000*i,5000*(i+1)
    #q = RemoteQuerySet('http://localhost:8000/api/','auth','user')
    #print q.count()
    #q.create(username=str(randint(1,100)))
    #print q.count()
    #print q.filter(username__icontains='t').count()
    #q.pprint()