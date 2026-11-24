from django.urls import path

from . import views

app_name = 'TODOlist'
urlpatterns = [
    # ex: /TODOlist/
    path('', views.TodolistView.as_view(), name='todolist'),
    # ex: /TODOlist/newtodo/
    path('newtodo/', views.TodoCreateView.as_view(), name='newtodo'),
    # ex: /TODOlist/5/results/
    path('<int:id>/results/', views.TodoDetailView.as_view(), name='results'),
    # TODO編集ページ
    path('<int:id>/edit/', views.TodoEditView.as_view(), name='edit'),
    # 編集内容をデータベースに保存
    path('<int:id>/update/', views.TodoUpdateView.as_view(), name='update'),
    # TODOを削除(GETは確認ページ、POSTで削除)
    path('<int:id>/delete/', views.TodoDeleteView.as_view(), name='delete'),
]
