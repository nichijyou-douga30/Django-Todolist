from django.urls import path

from . import views

app_name = 'TODOlist'
urlpatterns = [
    # ex: /TODOlist/
    path('', views.TodolistView.as_view(), name='todolist'),
    # ex: /TODOlist/5/results/
    path('<int:id>/results/', views.ResultsView, name='results'),
    # ex: /TODOlist/newtodo/
    path('newtodo/', views.NewtodoView, name='newtodo'),
    path('<int:id>/edit', views.edit, name='edit'), # TODO編集ページのURL
    path('<int:id>/update', views.update, name='update'), # 編集内容をデータベースに保存するURL
    path('<int:id>/delete', views.delete, name='delete'), # TODOを削除するURL
]