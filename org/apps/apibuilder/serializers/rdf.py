from django.core.serializers.python import Serializer as PythonSerializer
from rdflib import ConjunctiveGraph
from rdflib import BNode, Literal, BNode, Namespace, RDF
  
class Serializer(PythonSerializer):
    """
    Convert a queryset to RDF
    """    
    internal_use_only = False

    def end_serialization(self):
        FOAF = Namespace('http://xmlns.com/foaf/0.1/')
        DC = Namespace('http://purl.org/dc/elements/1.1/')
        
        self.graph = ConjunctiveGraph()
        self.options.pop('stream', None)
        fields = filter(None, self.options.pop('fields','').split(','))
        meta = None
        subject = None
        for object in self.objects:
            if not fields:
                fields = object['fields'].keys()    
            newmeta = object['model']
            if newmeta != meta:
                meta = newmeta
            subject = BNode('%s.%s'%(FOAF[newmeta],object['pk']))
            self.graph.add((subject,FOAF['pk'],Literal(object['pk'])))
            for k in fields:
                if k:
                    self.graph.add((subject,FOAF[k],Literal(object['fields'][k])))

    def getvalue(self):
        if callable(getattr(self.graph, 'serialize', None)):
            return self.graph.serialize()