from django.http import HttpResponse
from django.contrib.auth.models import Permission,User
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.core.cache import cache

from decorators import basicauth
from settings import *
from util import *
from models import *

class HttpError(HttpResponse):
    """500 Internal Error"""
    status_code,title = 500,'Internal Error'
    def __init__(self, request, msg):
        from models import QueryLog
        HttpResponse.__init__(self, '<h1>%s</h1><p>%s</p>'%(self.title,msg))
        if API_LOGGING:
            QueryLog.objects.create_from_transaction(request, self, msg)
        
class Forbidden(HttpError):
    """403 Response Forbidden Error"""
    status_code,title = 403,'Forbidden'

class BadRequest(HttpError):
    """400 Bad Request Error"""
    status_code,title = 400,'Bad Request'

def _delete(request, app_label, model, pk):
    """Delete the specified record"""
    # Validate start of request
    if not isinstance(request.user, User):
        return BadRequest(request, 'Anonymous commits are not allowed')
    if not (app_label and (model or pk)):
        return BadRequest(request, 'You must specify an resource to remove')

    if not Query(request).keychain.auth_commit(app_label,model,'delete'):
        return Forbidden(request,
            'You do not have permission to delete %s.%s'%(app_label,model))
    
    # Validate app/model
    model = get_model(app_label, model)
    if model is None:
        return BadRequest(request,
                'No model found for %s.%s'%(app_label,model))

    if pk:
        try:
            model.objects.get(pk=pk).delete()
        except model.DoesNotExist:
            return BadRequest(request, '%s with primary key %s not found' %
                              (model.__name__, pk))
    
        rpath = reverse(query,None,{'app_label':app_label,'model':model,'pk':pk})
        for key in cache.get('apibuilder-cache-keys', []):
            if key.split('--')[2] == rpath:
                cache.delete(key)
    else:
        try:
            model.objects.filter(**q.clean).exclude(**q.exclude).delete()
        except Exception, e:
            return HttpError(request, e)

    return HttpResponse('1', mimetype='text/plain')

def _commit(request, app_label, model, pk=None):
    """Update or Create a given model in an app from POST data"""   
    # Validate app/model
    model = get_model(app_label, model)
    if model is None:
        return BadRequest(request, 'No model found for %s.%s'%(app_label,model))

    q = Query(request)

    if pk:
        if not q.keychain.auth_commit(app_label, model,'change'):
            return Forbidden(request,
                'You do not have permission to change %s.%s'%(app_label,model))
        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return BadRequest(request, '%s with primary key %s not found'%
                              (model.__name__,pk))
        for attr,value in request.POST.items():
            try:
                setattr(obj, attr, value)
            except:
                continue
        
        try:
            obj.save(force_update=True)
        except Exception, e:
            return HttpError(request,
                        'Problem updating %s: %s' % (model.__name__,e))

        rpath = reverse(query,None,
                    {'app_label':app_label,'model':model,'pk':pk})
        for key in cache.get('apibuilder-cache-keys',[]):
            if key.split('--')[1] == rpath:
                cache.delete(key)
    else:
        if not q.keychain.auth_commit(app_label, model,'add'):
            return Forbidden(request,
                'You do not have permission to add %s.%s' % (app_label,model))
        try:
            obj = model.objects.create(**q.clean)
        except Exception, e:
            return HttpError(request, e)

    return HttpResponse(str(obj.pk), mimetype='text/plain')
   
def _query(request, app_label, model=None, queryset=None, pk=None, **serial_kw):
    """
    Serialized output of a given app model/queryset and request parameters
    """
    q,p = Query(request), Profile.objects.get_current()
    
    # Find the model/queryset
    if queryset:
        model = queryset.model
    elif model:
        model = get_model(app_label, model)
        if model is None:
            return BadRequest(request, 'No model found for %s.%s' %
                              (app_label,model))
        queryset = model.objects

    # Enforce allow,deny rules
    for arg in Profile.objects.get_current().eval('order'):
        option,criteria = arg.split(':')[:2]
        test = eval('%s_%s'%(option,criteria))(request)
        if option == 'deny' and test:
            return Forbidden(request, 'Operation not allowed')
        elif option == 'allow' and test:
            break
    
    # Catch JSONP calls through the callback param
    if Profile.objects.get_current().jsonp and Profile.objects.get_current().jsonp in q:
        q._format = 'json'
        q.pop('_',None) # No idea... ask jquery
        
    # Validates supported format
    try:
        mimetype = MimeType.objects.get(name=q._format, enabled=True)
    except MimeType.DoesNotExist:
        return BadRequest(request, "No format found matching %s" % q._format)

    response = HttpResponse(mimetype=mimetype.mimetype)

    # These are downloadable types
    if q._format in API_DOWNLOADABLES: 
        ext = q._format
        if ext == 'pickle': ext = 'pkl'
        elif ext == 'python': ext = 'py'
        response['Content-Disposition'] = 'attachment; filename=%s.%s.%s' % \
                            (app_label, model._meta.verbose_name, ext)

    # Hash each query for ca-ching!
    cache_key = q.cache_key(request, app_label, model)
    
    # Try loading from cache
    cached = cache.get(cache_key)
    if not cached is None:
        if Profile.objects.get_current().jsonp and Profile.objects.get_current().jsonp in q: # patch jsonp to match req
            cached = Profile.objects.get_current().jsonp + cached[cached.index('('):]
        response['Content-Length'] = str(len(cached))
        response.write(cached)
        return response
    
    # Compute authorization constraints
    q._fields = q.keychain.auth_fields(app_label, model, map(str, q._fields))
    qlim = int(q.keychain.limit.queryset_length)
    llim = int(q.keychain.limit.content_length)

    # Validate input query params
    if not qlim is None and qlim >= 0 and int(q._limit) - int(q._offset) > qlim:
        return BadRequest(request, 'Record limit exceded (%s)'%qlim)

    if model is None or q._fields is None:
        return BadRequest(request, 'Nothing matching criteria was found')

    # Filter/order queryset and fetch objects
    if pk:
        try:
            queryset = queryset.filter(pk=pk)
        except model.DoesNotExist:
            return BadRequest(request,
                    '%s with primary key %r not found' % (model.__name__, pk))
    else:
        if len(q):
            try:
                queryset = queryset.filter(**q.clean)
            except:
                return BadRequest(request, 'Invalid search parameters')
        if q._order_by:
            try:
                queryset = queryset.order_by(*q._order_by.split(','))
            except:
                return BadRequest(request, 'Invalid ordering parameters')
    
    # A little magic to work w/ RemoteQuerySet
    if q.exclude:
        queryset = queryset.exclude(**q.exclude)
    if not q._distinct is '':
        queryset = queryset.distinct(bool(q._distinct))
    if q._count:
        return HttpResponse(str(queryset.count()), 'text/plain')

    # Then slice
    try:
        queryset = queryset[q._offset:q._limit]
    except IndexError:
        return BadRequest(request, "No %s found matching the query" % \
                model._meta.verbose_name)        
        
    # Prepare content using specified serializer
    if len(q._fields):
        serial_kw['fields'] = ','.join(q._fields)
    if q._indent and q._format == 'json':
        serial_kw['indent'] = int(q._indent)
    if q._extras:
        serial_kw['extras'] = q._extras
    if q._relations:
        serial_kw['relations'] = q._relations

    try:
        content = model_transform(app_label, model,
                            q._format, queryset, **serial_kw)
    except Exception, e:
        return HttpError(request, e)    

    # Compress if needed
    if q._compression:
        import zlib
        if not  0 < int(q._compression) <= 9:
            return BadRequest(request, 'Invalid compression level')
        content = zlib.compress(content, int(q._compression))
    
    # JSONP callback wrapper
    if Profile.objects.get_current().jsonp and Profile.objects.get_current().jsonp in q: 
        content = '%s(%s)' % (Profile.objects.get_current().jsonp,content)
        
    # Calculate and validate response length
    content_length = len(content)
    if not llim is None and llim >= 0 and content_length > llim:
        return BadRequest(request, "Content length excedes limit %s" % llim)
    response['Content-Length'] = str(content_length)

    # Write content out and set cache
    response.write(content)
    cache.add(cache_key, content, q.keychain.cache_timeout(app_label, model))
    cache.set('apibuilder-cache-keys',
            cache.get('apibuilder-cache-keys',[]) + [cache_key])
    # Log sucessful transaction and yield response
    if API_LOGGING:
        QueryLog.objects.create_from_transaction(request, response, content[:100])
    return response

def method_dispatch(view_func):
    def wrapped(request, *a, **kw):
        if request.method == 'POST':
            return _commit(request, *a, **kw)
        elif request.method == 'DELETE':
            return _delete(request, *a, **kw)
        elif request.method == 'GET':
            return _query(request, *a, **kw)
        else:
            return BadRequest(request, 'Request method not permitted')
    def param_check(func):
        def wrapped(request, *a, **kw):
            #try:
            return func(request, *a, **kw)
            #except TypeError:
            #    return BadRequest(request, 'Resource not found!')
        return wrapped
    wrapped = param_check(wrapped)
    return wrapped

query = method_dispatch(_query)
auth_query = basicauth(Profile.objects.get_current().realm)(query)