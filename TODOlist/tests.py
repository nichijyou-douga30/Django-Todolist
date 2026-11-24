from datetime import timedelta

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import TodoForm
from .models import Todo, TodoEditHistory


def make_todo(theme='買い物', text='牛乳を買う'):
    return Todo.objects.create(Todo_theme=theme, Todo_text=text)


class TodoModelTests(TestCase):
    def setUp(self):
        self.todo = make_todo()

    def test_str_is_theme(self):
        self.assertEqual(str(self.todo), '買い物')

    def test_new_todo_is_not_edited(self):
        self.assertTrue(self.todo.Edit_flag)
        self.assertFalse(self.todo.is_edited)

    def test_record_edit_returns_none_when_unchanged(self):
        self.assertIsNone(self.todo.record_edit('買い物', '牛乳を買う'))
        self.assertFalse(self.todo.is_edited)
        self.assertEqual(TodoEditHistory.objects.count(), 0)

    def test_record_edit_saves_history_when_changed(self):
        self.todo.Todo_text = '牛乳と卵を買う'
        history = self.todo.record_edit('買い物', '牛乳を買う')

        self.assertIsNotNone(history)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_edited)
        self.assertEqual(self.todo.Todo_text, '牛乳と卵を買う')
        self.assertEqual(history.previous_text, '牛乳を買う')
        self.assertEqual(history.new_text, '牛乳と卵を買う')

    def test_history_str(self):
        history = TodoEditHistory(previous_theme='A', new_theme='B')
        self.assertEqual(str(history), 'A → B')


class TodoFormTests(TestCase):
    def test_valid(self):
        form = TodoForm({'Todo_theme': '買い物', 'Todo_text': '牛乳'})
        self.assertTrue(form.is_valid())

    def test_theme_is_required(self):
        form = TodoForm({'Todo_theme': '', 'Todo_text': '牛乳'})
        self.assertFalse(form.is_valid())
        self.assertIn('Todo_theme', form.errors)

    def test_text_is_required(self):
        form = TodoForm({'Todo_theme': '買い物', 'Todo_text': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('Todo_text', form.errors)

    def test_whitespace_only_is_rejected(self):
        form = TodoForm({'Todo_theme': '   ', 'Todo_text': '牛乳'})
        self.assertFalse(form.is_valid())

    def test_theme_max_length(self):
        form = TodoForm({'Todo_theme': 'あ' * 201, 'Todo_text': '牛乳'})
        self.assertFalse(form.is_valid())
        self.assertTrue(TodoForm({'Todo_theme': 'あ' * 200, 'Todo_text': '牛乳'}).is_valid())


class TodolistViewTests(TestCase):
    def test_empty_list(self):
        response = self.client.get(reverse('TODOlist:todolist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TODOはまだありません')
        self.assertNotContains(response, 'id="delete-dialog"')

    def test_newest_first(self):
        now = timezone.now()
        old = make_todo('古い', 'a')
        new = make_todo('新しい', 'b')
        # pub_dateはauto_nowなので、updateで直接上書きする
        Todo.objects.filter(pk=old.pk).update(pub_date=now - timedelta(days=1))
        Todo.objects.filter(pk=new.pk).update(pub_date=now)

        response = self.client.get(reverse('TODOlist:todolist'))
        self.assertEqual(
            [t.Todo_theme for t in response.context['latest_todo_list']],
            ['新しい', '古い'],
        )

    def test_pagination_five_per_page(self):
        for i in range(7):
            make_todo(f'TODO{i}', 'text')

        page1 = self.client.get(reverse('TODOlist:todolist'))
        page2 = self.client.get(reverse('TODOlist:todolist'), {'page': 2})
        self.assertEqual(len(page1.context['latest_todo_list']), 5)
        self.assertEqual(len(page2.context['latest_todo_list']), 2)
        self.assertContains(page1, '?page=2')
        self.assertContains(page2, '?page=1')

    def test_no_pagination_links_for_single_page(self):
        make_todo()
        response = self.client.get(reverse('TODOlist:todolist'))
        self.assertNotContains(response, '?page=')

    def test_out_of_range_page_is_404(self):
        make_todo()
        response = self.client.get(reverse('TODOlist:todolist'), {'page': 99})
        self.assertEqual(response.status_code, 404)

    def test_list_has_delete_dialog_and_links(self):
        todo = make_todo()
        response = self.client.get(reverse('TODOlist:todolist'))
        self.assertContains(response, 'id="delete-dialog"')
        self.assertContains(response, f'href="{reverse("TODOlist:delete", args=[todo.pk])}"')
        self.assertContains(response, 'data-delete-title="買い物"')


class TodoCreateViewTests(TestCase):
    def test_get_shows_form(self):
        response = self.client.get(reverse('TODOlist:newtodo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="Todo_theme"')

    def test_post_creates_todo_and_redirects(self):
        response = self.client.post(
            reverse('TODOlist:newtodo'),
            {'Todo_theme': '掃除', 'Todo_text': '部屋を掃除する'},
        )
        self.assertRedirects(response, reverse('TODOlist:todolist'))
        todo = Todo.objects.get()
        self.assertEqual(todo.Todo_theme, '掃除')
        self.assertTrue(todo.Edit_flag)
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ['TODOを登録しました'],
        )

    def test_invalid_post_shows_error_and_creates_nothing(self):
        response = self.client.post(
            reverse('TODOlist:newtodo'),
            {'Todo_theme': '', 'Todo_text': '部屋を掃除する'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TODOが不正です')
        self.assertEqual(Todo.objects.count(), 0)


class TodoDetailViewTests(TestCase):
    def test_shows_todo(self):
        todo = make_todo()
        response = self.client.get(reverse('TODOlist:results', args=[todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '買い物')
        self.assertContains(response, '牛乳を買う')

    def test_missing_todo_is_404(self):
        response = self.client.get(reverse('TODOlist:results', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_has_delete_dialog(self):
        todo = make_todo()
        response = self.client.get(reverse('TODOlist:results', args=[todo.pk]))
        self.assertContains(response, 'id="delete-dialog"')
        self.assertContains(response, 'class="btn btn-danger js-delete"')
        self.assertContains(response, 'delete_dialog.js')


class EditHistoryTests(TestCase):
    def setUp(self):
        self.todo = make_todo()

    def test_new_todo_is_not_edited_and_has_no_history(self):
        self.assertTrue(self.todo.Edit_flag)
        self.assertFalse(self.todo.is_edited)
        self.assertEqual(self.todo.edit_histories.count(), 0)

        response = self.client.get(reverse('TODOlist:results', args=[self.todo.pk]))
        self.assertNotContains(response, '編集済み')
        self.assertContains(response, '編集履歴はありません。')

        list_response = self.client.get(reverse('TODOlist:todolist'))
        self.assertContains(list_response, '買い物')
        self.assertNotContains(list_response, '編集済み')

    def test_update_records_history_and_shows_edited_badge(self):
        response = self.client.post(
            reverse('TODOlist:update', args=[self.todo.pk]),
            {'Todo_theme': '買い物', 'Todo_text': '牛乳と卵を買う'},
        )
        self.assertRedirects(
            response,
            reverse('TODOlist:results', args=[self.todo.pk]),
        )

        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_edited)
        history = TodoEditHistory.objects.get(todo=self.todo)
        self.assertEqual(history.previous_theme, '買い物')
        self.assertEqual(history.previous_text, '牛乳を買う')
        self.assertEqual(history.new_theme, '買い物')
        self.assertEqual(history.new_text, '牛乳と卵を買う')
        self.assertIsNotNone(history.edited_at)

        results = self.client.get(reverse('TODOlist:results', args=[self.todo.pk]))
        self.assertContains(results, '編集済み')
        self.assertContains(results, '変更前内容: 牛乳を買う')
        self.assertContains(results, '変更後内容: 牛乳と卵を買う')

        listing = self.client.get(reverse('TODOlist:todolist'))
        self.assertContains(listing, '編集済み')

        edit_page = self.client.get(reverse('TODOlist:edit', args=[self.todo.pk]))
        self.assertContains(edit_page, '編集済み')
        self.assertContains(edit_page, '変更前内容: 牛乳を買う')
        self.assertContains(edit_page, 'value="買い物"')

    def test_second_edit_keeps_newest_history_first(self):
        self.client.post(
            reverse('TODOlist:update', args=[self.todo.pk]),
            {'Todo_theme': '週末の買い物', 'Todo_text': '牛乳を買う'},
        )
        self.client.post(
            reverse('TODOlist:update', args=[self.todo.pk]),
            {'Todo_theme': '週末の買い物', 'Todo_text': 'パンも買う'},
        )

        histories = list(self.todo.edit_histories.all())
        self.assertEqual(len(histories), 2)
        self.assertEqual(histories[0].previous_text, '牛乳を買う')
        self.assertEqual(histories[0].new_text, 'パンも買う')
        self.assertEqual(histories[1].previous_theme, '買い物')
        self.assertEqual(histories[1].new_theme, '週末の買い物')

        results = self.client.get(reverse('TODOlist:results', args=[self.todo.pk]))
        content = results.content.decode()
        self.assertLess(
            content.index('変更後内容: パンも買う'),
            content.index('変更前テーマ: 買い物'),
        )

    def test_unchanged_save_does_not_record_history(self):
        response = self.client.post(
            reverse('TODOlist:update', args=[self.todo.pk]),
            {'Todo_theme': '買い物', 'Todo_text': '牛乳を買う'},
        )
        self.assertRedirects(
            response,
            reverse('TODOlist:results', args=[self.todo.pk]),
        )
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.is_edited)
        self.assertEqual(TodoEditHistory.objects.count(), 0)

    def test_invalid_update_does_not_record_history(self):
        response = self.client.post(
            reverse('TODOlist:update', args=[self.todo.pk]),
            {'Todo_theme': '', 'Todo_text': '牛乳を買う'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'データが不正です')
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.Todo_theme, '買い物')
        self.assertFalse(self.todo.is_edited)
        self.assertEqual(TodoEditHistory.objects.count(), 0)

    def test_get_update_redirects_to_edit(self):
        response = self.client.get(reverse('TODOlist:update', args=[self.todo.pk]))
        self.assertRedirects(response, reverse('TODOlist:edit', args=[self.todo.pk]))

    def test_edit_page_rejects_post(self):
        response = self.client.post(
            reverse('TODOlist:edit', args=[self.todo.pk]),
            {'Todo_theme': '変更', 'Todo_text': '変更'},
        )
        self.assertEqual(response.status_code, 405)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.Todo_theme, '買い物')

    def test_edit_and_update_missing_todo_is_404(self):
        self.assertEqual(
            self.client.get(reverse('TODOlist:edit', args=[999])).status_code, 404)
        self.assertEqual(
            self.client.post(reverse('TODOlist:update', args=[999]), {
                'Todo_theme': 'a', 'Todo_text': 'b'}).status_code, 404)


class TodoDeleteViewTests(TestCase):
    def setUp(self):
        self.todo = make_todo()

    def test_get_shows_confirmation_page_without_deleting(self):
        response = self.client.get(reverse('TODOlist:delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '削除しますか')
        self.assertContains(response, '買い物')
        self.assertEqual(Todo.objects.count(), 1)

    def test_post_deletes_and_shows_message(self):
        response = self.client.post(
            reverse('TODOlist:delete', args=[self.todo.pk]), follow=True)
        self.assertRedirects(response, reverse('TODOlist:todolist'))
        self.assertEqual(Todo.objects.count(), 0)
        self.assertContains(response, '「買い物」を削除しました')

    def test_deleting_todo_deletes_history(self):
        self.todo.Todo_text = '卵も買う'
        self.todo.record_edit('買い物', '牛乳を買う')
        self.assertEqual(TodoEditHistory.objects.count(), 1)

        response = self.client.post(reverse('TODOlist:delete', args=[self.todo.pk]))
        self.assertRedirects(response, reverse('TODOlist:todolist'))
        self.assertEqual(Todo.objects.count(), 0)
        self.assertEqual(TodoEditHistory.objects.count(), 0)

    def test_missing_todo_is_404(self):
        self.assertEqual(
            self.client.get(reverse('TODOlist:delete', args=[999])).status_code, 404)
        self.assertEqual(
            self.client.post(reverse('TODOlist:delete', args=[999])).status_code, 404)
