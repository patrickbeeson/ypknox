from django import template
from ypknox.apps.news.models import PressRelease

class PressReleaseYearListNode(template.Node):
	def __init__(self, varname):
		self.varname = varname
	
	def render(self, context):
		context[self.varname] = PressRelease.live.dates("pub_date", "year")
		return ''

def do_get_pressrelease_year_list(parser, token):
	"""
	Gets a list of years in which press releases are published.
	
	Syntax::
	
		{% get_pressrelease_year_list as [varname] %}
		
	Example::
	
		{% get_pressrelease_year_list as year_list %}
	"""
	bits = token.contents.split()
	if len(bits) != 3:
		raise template.TemplateSyntaxError, "'%s' tag takes two arguements" % bits[0]
	if bits[1] != "as":
		raise template.TemplateSyntaxError, "First arguement to '%s' tag must be 'as'" % bits[0]
	return PressReleaseYearListNode(bits[2])

class PressReleaseMonthListNode(template.Node):
	def __init__(self, varname):
		self.varname = varname
	
	def render(self, context):
		context[self.varname] = PressRelease.live.dates("pub_date", "month")
		return ''

def do_get_pressrelease_month_list(parser, token):
	"""
	Gets a list of months in which press releases are published.
	
	Syntax::
	
		{% get_pressrelease_month_list as [varname] %}
		
	Example::
	
		{% get_pressrelease_month_list as month_list %}
	"""
	bits = token.contents.split()
	if len(bits) != 3:
		raise template.TemplateSyntaxError, "'%s' tag takes two arguements" % bits[0]
	if bits[1] != "as":
		raise template.TemplateSyntaxError, "First arguement to '%s' tag must be 'as'" % bits[0]
	return PressReleaseMonthListNode(bits[2])
	
register = template.Library()
register.tag('get_pressrelease_month_list', do_get_pressrelease_month_list)
register.tag('get_pressrelease_year_list', do_get_pressrelease_year_list)