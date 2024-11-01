from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView
from . import models


# Create your views here.

class TaskListClass(TemplateView):
    template_name = 'tasklist.html'

class IventList(ListView):
    context_object_name = 'Ivent_list'
    model = models.Ivents
    
def index(request):
    return render(request, "tasklist.html")

