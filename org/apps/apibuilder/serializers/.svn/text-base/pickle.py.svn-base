from django.core.serializers.python import Serializer as PythonSerializer
try:
    import cPickle as pickle
except ImportError:
    import pickle
    
class Serializer(PythonSerializer):
    """
    Convert a queryset to Pickle 
    """    
    internal_use_only = False

    def getvalue(self):
        return pickle.dumps(self.objects,self.options.pop('protocol',pickle.HIGHEST_PROTOCOL))