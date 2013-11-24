from django.core.serializers import register_serializer
from django.http import HttpResponse

import settings



def get_ip(request):
    """Get remote address of client"""
    return request.META.get('REMOTE_ADDR',
        request.META.get('HTTP_X_FORWARDED_FOR',None))

def cmp_ip(ip1,ip2): 
    """
    Returns True when the IP patterns match, % is a wildcard
    
    >>> cmp_ip('127.0.0.1','127.0.0.%')
    True
    >>> cmp_ip('127.0.0.1','127.0.0.0')
    False
    """
    ip1 = ip1.replace('%','').split('.')
    ip2 = ip2.replace('%','').split('.')
    for i in range(4): 
        if ip1[i] and ip2[i] and ip1[i] != ip2[i]:
            return False
    return True

class Transformer(dict):
    def __init__(self):
        dict.__init__(self, settings.API_TRANSFORMS.copy())
    
    def register(self, app_model, module_func):
        """Register a transformer for a given app_model
        The module_func may either be a function or a str
        
        >>> def optimus_transformer(autobot):
        ...    if autobot.name == 'optimus':
        ...        autobot.body = 'truck' # change into a truck http://twurl.nl/l5exg4
        ...    return autobot
        ...
        >>> register_transform('transformers.autobots', optimus_transformer)
        """
        if callable(module_func):
            mod = module_func
        else:
            mod = __import__(module_func)
        
            for bit in module_func.split('.')[1:]:
                mod = getattr(mod, bit)
        
        if app_model in self:
            self[app_model] += (mod,)
        else:
            self[app_model] = (mod,)

    def get_for_model(self, app_model):
        try:
            return self[app_model]
        except KeyError:
            return ()
        
transform = Transformer()        

# Django's
register_serializer("xml", "django.core.serializers.xml_serializer")

# Wad O' Stuff
register_serializer("python","apibuilder.wadofstuff.python")
register_serializer("json", "apibuilder.wadofstuff.json")

# Extras
register_serializer('html','apibuilder.serializers.html')
register_serializer('csv','apibuilder.serializers.csv_')
register_serializer('pickle','apibuilder.serializers.pickle')

try:
    register_serializer("yaml", "django.core.serializers.pyyaml")
except ImportError:
    pass
try:
    register_serializer('rdf','apibuilder.serializers.rdf')
except ImportError:
    pass
try:
    register_serializer('amf','apibuilder.serializers.amf')
except ImportError:
    pass
