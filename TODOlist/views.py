from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from .forms import Todoform
from .models import Todo


class TodolistView(generic.ListView):
    template_name = 'TODOlist/todolist.html'
    context_object_name = 'latest_todo_list'
    paginate_by = 5

    def get_queryset(self):
        """Return the last five published Todos"""
        return Todo.objects.order_by('-pub_date')


def ResultsView(request, id):
    todo = get_object_or_404(
        Todo.objects.prefetch_related('edit_histories'),
        pk=id,
    )
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
    return render(request, "TODOlist/newtodo.html", {'form': form})


def edit(request, id):
    todo = get_object_or_404(
        Todo.objects.prefetch_related('edit_histories'),
        pk=id,
    )
    todoForm = Todoform(instance=todo)
    context = {
        'todo': todo,
        'todoForm': todoForm,
    }
    return render(request, 'TODOlist/edit.html', context)


def update(request, id):
    todo = get_object_or_404(Todo, pk=id)
    if request.method != 'POST':
        return redirect('TODOlist:edit', id=id)

    previous_theme = todo.Todo_theme
    previous_text = todo.Todo_text
    todo_form = Todoform(request.POST, instance=todo)
    if todo_form.is_valid():
        todo_form.save(commit=False)
        todo.record_edit(previous_theme, previous_text)
        return redirect('TODOlist:results', id=todo.id)

    messages.error(request, 'データが不正です')
    todo.refresh_from_db()
    context = {
        'todo': todo,
        'todoForm': todo_form,
    }
    return render(request, 'TODOlist/edit.html', context)


def delete(request, id):
    if request.method == "POST":
        todo = get_object_or_404(Todo, pk=id)
        todo.delete()
        messages.success(request, '削除しました')
        return redirect('TODOlist:todolist')
    else:
        return render(request, 'TODOlist/delete.html')
