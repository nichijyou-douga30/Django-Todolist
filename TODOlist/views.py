from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Todo
from .forms import todoform
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

# Create your views here.
class TodolistView(generic.ListView):
    template_name = 'TODOlist/todolist.html'
    context_object_name = 'latest_todo_list'
    paginate_by = 5

    def get_queryset(self):
        """Return the last five published Todos"""
        return Todo.objects.order_by('-pub_date')

class ResultsView(generic.DetailView):
    model = Todo
    template_name = 'TODOlist/results.html'

class NewtodoView(FormView):
    template_name = 'TODOlist/newtodo.html'
    form_class = todoform
    success_url = reverse_lazy('TODOlist:todolist')
    def form_valid(self, form):
        self.object = comment = form.save()
        messages.success(self.request, 'TODOを登録しました')
        return redirect(self.get_success_url())