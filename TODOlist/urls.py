from django.urls import path

from . import views

app_name = 'TODOlist'
urlpatterns = [
    # ex: /TODOlist/
    path('', views.TodolistView.as_view(), name='todolist'),
    # ex: /TODOlist/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('newtodo/', views.newtodo, name='newtodo'),
    # ex: /TODOlist/newtodo/
    path('newtodo/', views.NewtodoView.as_view(), name='newtodo'),
]