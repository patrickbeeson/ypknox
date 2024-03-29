"""
A base contact form for allowing users to send email messages through
a web interface, and a subclass demonstrating useful functionality.

"""


#<<<<<<< .mine
import sha

#from django import forms
#=======
from django import forms
#>>>>>>> .r50
from django.conf import settings
# I'm using a modified version of django.core.mail to allow for TLS timeout | CHANGED 5/09/08 TO USE WEBFACTION INSTEAD
#from contact_form.mail_mod_tls import send_mail
from django.core.mail import send_mail
from django.template import loader, RequestContext
from django.contrib.sites.models import Site


# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary.
attrs_dict = { 'class': 'required' }


class ContactForm(forms.Form):
    """
    Base contact form class from which all contact form classes should
    inherit.
    
    If you don't need any custom functionality, you can simply use
    this form to provide basic contact functionality; it will collect
    name, email address and message.
    
    The ``contact_form`` view included in this application knows how
    to work with this form and can handle many types of subclasses as
    well (see below for a discussion of the important points), so in
    many cases it will be all that you need. If you'd like to use this
    form or a subclass of it from one of your own views, just do the
    following:
    
        1. When you instantiate the form, pass the current
           ``HttpRequest`` object to the constructor as the keyword
           argument ``request``; this is used internally by the base
           implementation, and also made available so that subclasses
           can add functionality which relies on inspecting the
           request.
           
        2. To send the message, call the form's ``save`` method, which
           accepts the keyword argument ``fail_silently`` and defaults
           it to ``False``. This argument is passed directly to
           ``send_mail``, and allows you to suppress or raise
           exceptions as needed for debugging. The ``save`` method has
           no return value.
           
    Other than that, treat it like any other form; validity checks and
    validated data are handled normally, through the ``is_valid``
    method and the ``cleaned_data`` dictionary.
    
    
    Base implementation
    -------------------
    
    Under the hood, this form uses a somewhat abstracted interface in
    order to make it easier to subclass and add functionality. There
    are several important attributes subclasses may want to look at
    overriding, all of which will work (in the base implementation) as
    either plain attributes or as callable methods:
    
        * ``from_email`` -- used to get the address to use in the
          ``From:`` header of the message. The base implementation
          returns the value of the ``DEFAULT_FROM_EMAIL`` setting.
          
        * ``message`` -- used to get the message body as a string. The
          base implementation renders a template using the form's
          ``cleaned_data`` dictionary as context.
          
        * ``recipient_list`` -- used to generate the list of
          recipients for the message. The base implementation returns
          the email addresses specified in the ``MANAGERS`` setting.
          
        * ``subject`` -- used to generate the subject line for the
          message. The base implementation returns the string 'Message
          sent through the web site', with the name of the current
          ``Site`` prepended.
          
        * ``template_name`` -- used by the base ``message`` method to
          determine which template to use for rendering the
          message. Default is ``contact_form/contact_form.txt``.
          
    Internally, the base implementation ``_get_message_dict`` method
    collects ``from_email``, ``message``, ``recipient_list`` and
    ``subject`` into a dictionary, which the ``save`` method then
    passes directly to ``send_mail`` as keyword arguments.
    
    Particularly important is the ``message`` attribute, with its base
    implementation as a method which renders a template; because it
    passes ``cleaned_data`` as the template context, any additional
    fields added by a subclass will automatically be available in the
    template. This means that many useful subclasses can get by with
    just adding a few fields and possibly overriding
    ``template_name``.
    
    Much useful functionality can be achieved in subclasses without
    having to override much of the above; adding additional validation
    methods works the same as any other form, and typically only a few
    items -- ``recipient_list`` and ``subject_line``, for example,
    need to be overridden to achieve customized behavior.
    
    
    Other notes for subclassing
    ---------------------------
    
    Subclasses which want to inspect the current ``HttpRequest`` to
    add functionality can access it via the attribute ``request``; the
    base ``message`` takes advantage of this to use ``RequestContext``
    when rendering its template. See the ``AkismetContactForm``
    subclass in this file for an example of using the request to
    perform additional validation.
    
    Subclasses which override ``__init__`` need to accept ``*args``
    and ``**kwargs``, and pass them via ``super`` in order to ensure
    proper behavior.
    
    Subclasses should be careful if overriding ``_get_message_dict``,
    since that method **must** return a dictionary suitable for
    passing directly to ``send_mail`` (unless ``save`` is overridden
    as well).
    
    Overriding ``save`` is relatively safe, though remember that code
    which uses your form will expect ``save`` to accept the
    ``fail_silently`` keyword argument. In the base implementation,
    that argument defaults to ``False``, on the assumption that it's
    far better to notice errors than to silently not send mail from
    the contact form (see also the Zen of Python: "Errors should never
    pass silently, unless explicitly silenced").
    
    """
    def __init__(self, data=None, files=None, request=None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        super(ContactForm, self).__init__(data=data, files=files, *args, **kwargs)
        self.request = request
    
    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs=attrs_dict),
                           label=u'Your name')
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=200)),
                             label=u'Your email address')
    body = forms.CharField(widget=forms.Textarea(attrs=attrs_dict),
                              label=u'Your message')
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    recipient_list = [mail_tuple[1] for mail_tuple in settings.MANAGERS]
    
    subject = "[%s] Message sent through the web site" % Site.objects.get_current().name
    
    template_name = 'contact_form/contact_form.txt'
    
    def message(self):
        """
        Renders the body of the message to a string.
        
        """
        if callable(self.template_name):
            template_name = self.template_name()
        else:
            template_name = self.template_name
        t = loader.get_template(template_name)
        return t.render(RequestContext(self.request, self.cleaned_data))
    
    def _get_message_dict(self):
        if not self.is_valid():
            raise ValueError("Message cannot be sent from invalid contact form")
        message_dict = {}
        for message_part in ('from_email', 'message', 'recipient_list', 'subject'):
            attr = getattr(self, message_part)
            message_dict[message_part] = callable(attr) and attr() or attr
        return message_dict
    
    def save(self, fail_silently=False):
        """
        Builds and sends the email message.
        
        """
        send_mail(fail_silently=fail_silently, **self._get_message_dict())


class AkismetContactForm(ContactForm):
    """
    Contact form which doesn't add any extra fields, but does add an
    Akismet spam check to the validation routine.
    
    Requires the setting ``AKISMET_API_KEY``, which should be a valid
    Akismet API key.
    
    """
    def clean_body(self):
        if 'body' in self.cleaned_data and hasattr(settings, 'AKISMET_API_KEY') and settings.AKISMET_API_KEY:
            from akismet import Akismet
            akismet_api = Akismet(key=settings.AKISMET_API_KEY,
                                  blog_url='http://%s/' % Site.objects.get_current().domain)
            if akismet_api.verify_key():
                akismet_data = { 'comment_type': 'comment',
                                 'referer': self.request.META.get('HTTP_REFERER', ''),
                                 'user_ip': self.request.META.get('REMOTE_ADDR', ''),
                                 'user_agent': self.request.META.get('HTTP_USER_AGENT', '') }
                if akismet_api.comment_check(self.cleaned_data['body'], data=akismet_data, build_data=True):
                    raise forms.ValidationError(u"Akismet thinks this message is spam")
        return self.cleaned_data['body']
