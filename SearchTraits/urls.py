from django.urls import path
from django.conf import urls
from . import views

urlpatterns = [
    path("index", views.index, name="indexs"),
    path("old", views.SearchTraitsForm_2021Ver, name="SearchTraitsForm"),
    path("badge", views.BadgeForm, name="BadgeForm"),
    path("combination", views.CombinationListView, name="CombinationListView"),
    path("detail", views.DetailView, name="DetailView"),
    path("", views.ListView, name="SearchTraitsForm"),
]

urls.handler404 = views.index