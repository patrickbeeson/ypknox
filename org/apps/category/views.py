from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.list_detail import object_list
from ypknox.apps.events.models import Event
from ypknox.apps.news.models import PressRelease
from ypknox.apps.category.models import Category

def category_detail(request, slug):
	category = get_object_or_404(Category, slug=slug)
	return render_to_response('category/category_detail.html',
								{ 'object_list': category.live_pressrelease_set() })

