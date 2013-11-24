from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User,get_hexdigest
from base64 import b64decode

from models import Key
from apibuilder import get_ip

def view_or_basicauth(view, request, realm = "", *args, **kwargs):
    if request.user.is_authenticated():
        return view(request, *args, **kwargs)
    auth = request.META.get('HTTP_AUTHORIZATION','').split()
    if len(auth) == 2 and auth[0].lower() == 'basic':
        try: # Browser based Auth
            uname, passwd = b64decode(auth[1]).split(':')
            user = authenticate(username=uname, password=passwd)
            if user != None and user.is_active:
                login(request, user) # ORLY?
                request.user = user
                return view(request, *args, **kwargs)
        except ValueError: # Can has Keyed Auth ????
            hash = b64decode(auth[1]) 
            try:
                host = get_ip(request)
                # Does key exist?
                user = Key.objects.get(key=hash,hostname=host).user
                # Does hash match?
                assert hash == get_hexdigest('sha1', host, user.username)
                # Then login if active
                if user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' 
                    login(request, user) # ORLY?
                    return view(request, *args, **kwargs)
            except (AssertionError, Key.DoesNotExist):
                # WTF!
                pass
    # NO WAI!!!
    response = HttpResponse('Not authorized')
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response

def basicauth(realm = ""):
    def view_decorator(func, **kw):
        def wrapper(request, *args, **kwargs):
            kwargs.update(kw)
            return view_or_basicauth(func, request, realm, *args, **kwargs)
        return wrapper
    return view_decorator