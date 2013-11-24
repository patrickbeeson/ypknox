from django.core.serializers.python import Serializer as PythonSerializer

class Serializer(PythonSerializer):
    """
    Convert a queryset to HTML
    """
    internal_use_only = False

    def end_serialization(self):
        self.options.pop('stream', None)
        fields = filter(None, self.options.pop('fields','').split(','))
        meta = None
        for object in self.objects:
            if not fields:
                fields = object['fields'].keys()    
            newmeta = object['model']
            if newmeta != meta:
                meta = newmeta
                self.stream.write('<h3>%s</h3>'%meta)
                self.stream.write('<tr>%s</tr>'%''.join(['<th>%s</th>'%x for x in ['pk'] + fields]))
            self.stream.write('<tr>%s</tr>'%''.join(['<td>%s</td>'%object['pk']] + ['<td>%s</td>'%object['fields'][k] for k in fields if k]))

    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return '<table>%s</table>'%self.stream.getvalue()