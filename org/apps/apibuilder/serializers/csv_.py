from django.core.serializers.python import Serializer as PythonSerializer
import csv

class Serializer(PythonSerializer):
    """
    Convert a queryset to CSV
    """
    internal_use_only = False

    def end_serialization(self):
        self.options.pop('stream', None)
        fields = filter(None, self.options.pop('fields','').split(','))
        writer = csv.writer(self.stream, **self.options)
        meta = None
        for object in self.objects:
            if not fields:
                fields = object['fields'].keys()    
            newmeta = object['model']
            if newmeta != meta:
                meta = newmeta
                writer.writerow(['pk'] + fields)
            writer.writerow([object['pk']] + [object['fields'][k] for k in fields if k])

    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()


