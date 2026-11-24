from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from .forms import TodoForm
from .models import Todo


class TodolistView(generic.ListView):
    """TODO一覧(新しい順、5件ずつ)。"""
    model = Todo
    template_name = 'TODOlist/todolist.html'
    context_object_name = 'latest_todo_list'
    paginate_by = 5
    # pub_dateが同時刻でも順序が変わらないよう、pkを第2キーにする
    ordering = ['-pub_date', '-pk']


class TodoDetailView(generic.DetailView):
    """TODOの詳細と編集履歴。"""
    queryset = Todo.objects.prefetch_related('edit_histories')
    template_name = 'TODOlist/results.html'
    pk_url_kwarg = 'id'
    context_object_name = 'todo'


class TodoCreateView(generic.CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'TODOlist/newtodo.html'
    success_url = reverse_lazy('TODOlist:todolist')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'TODOを登録しました')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'TODOが不正です')
        return super().form_invalid(form)


class TodoEditView(generic.UpdateView):
    """編集フォームの表示(GETのみ)。保存はTodoUpdateViewが受け持つ。"""
    queryset = Todo.objects.prefetch_related('edit_histories')
    form_class = TodoForm
    template_name = 'TODOlist/edit.html'
    pk_url_kwarg = 'id'
    context_object_name = 'todo'
    http_method_names = ['get', 'head', 'options']

    def get_success_url(self):
        return reverse('TODOlist:results', args=[self.object.pk])


class TodoUpdateView(TodoEditView):
    """編集内容の保存(POSTのみ)。変更があったときだけ履歴を残す。"""
    http_method_names = ['get', 'post', 'head', 'options']

    def get(self, request, *args, **kwargs):
        return redirect('TODOlist:edit', id=kwargs['id'])

    def form_valid(self, form):
        # form.initialはフォーム生成時(=変更前)のDBの値
        form.instance.record_edit(
            previous_theme=form.initial['Todo_theme'],
            previous_text=form.initial['Todo_text'],
        )
        self.object = form.instance
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'データが不正です')
        # ModelFormの検証で書き換わったインスタンスをDBの状態に戻す
        self.object.refresh_from_db()
        return super().form_invalid(form)


class TodoDeleteView(generic.DeleteView):
    """GET: JavaScriptが使えない場合の確認ページ / POST: 削除。"""
    model = Todo
    template_name = 'TODOlist/delete.html'
    pk_url_kwarg = 'id'
    context_object_name = 'todo'
    success_url = reverse_lazy('TODOlist:todolist')

    def post(self, request, *args, **kwargs):
        # Djangoのバージョン差(DeleteViewのform化)に依存しないよう、postで直接処理する
        self.object = self.get_object()
        title = self.object.Todo_theme
        self.object.delete()
        messages.success(request, f'「{title}」を削除しました')
        return redirect(self.success_url)
