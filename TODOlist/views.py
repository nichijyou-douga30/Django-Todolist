from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Todo
from .forms import Todoform
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.shortcuts import render,get_object_or_404

# Create your views here.
class TodolistView(generic.ListView):
    template_name = 'TODOlist/todolist.html'
    context_object_name = 'latest_todo_list'
    paginate_by = 5

    def get_queryset(self):
        """Return the last five published Todos"""
        return Todo.objects.order_by('-pub_date')

def ResultsView(request,id):
    todo = get_object_or_404(Todo, pk=id)
    if todo.Edit_flag:
        messages.info(request, 'newresult')
    else:
        messages.info(request, 'editedresult')
    context = {
        'todo': todo,
    }
    return render(request, 'TODOlist/results.html', context)

def NewtodoView(request):
    if request.method == "POST":
        form = Todoform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('TODOlist:todolist')
        else:
            messages.error(request, 'TODOが不正です')
    else:
        form = Todoform()
    context = {
    "form": form
    }
    return render(request, "TODOlist/newtodo.html", {'form': form})
    
# TODO編集ページedit関数
def edit(request, id):
    todo = get_object_or_404(Todo, pk=id) # 指定したTODOをtodoに代入
    todoForm = Todoform
    context = {
        'todo': todo,
        'todoForm': todoForm,
    }
    return render(request, 'TODOlist/edit.html', context)

# 編集データを保存して結果ページに行くupdate関数
def update(request, id):
    # リクエストのメソッドがPOSTなら
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=id)
        todo.Edit_flag = False
        #「編集済み」メッセージの設定
        if todo.Edit_flag:
            messages.info(request, 'newresult')
        else:
            messages.info(request, 'editedresult')
        todoForm = Todoform(request.POST, instance=todo) # TodoFormクラスからtodoFormオブジェクトを生成
        # 受け取ったデータが正常なら
        if todoForm.is_valid():
            todoForm.save() # データを保存
        else:
            messages.error(request, 'データが不正です')
    context = {
        'todo': todo
    }
    return render(request, 'TODOlist/results.html', context) # 結果ページに行く

# TODOを削除するdelete関数
def delete(request, id):
    if request.method == "POST":
        todo = get_object_or_404(Todo, pk=id) # 指定したTODOをtodoに代入
        todo.delete()
        messages.success(request, '削除しました')
        return redirect('TODOlist:todolist')
    else:
        return render(request, 'TODOlist/delete.html')