from django.test import TestCase
from django.urls import reverse

from .models import Todo, TodoEditHistory


class EditHistoryTests(TestCase):
    def setUp(self):
        self.todo = Todo.objects.create(
            Todo_theme='買い物',
            Todo_text='牛乳を買う',
        )

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

    def test_deleting_todo_deletes_history(self):
        self.todo.Todo_text = '卵も買う'
        self.todo.record_edit('買い物', '牛乳を買う')
        self.assertEqual(TodoEditHistory.objects.count(), 1)

        response = self.client.post(reverse('TODOlist:delete', args=[self.todo.pk]))
        self.assertRedirects(response, reverse('TODOlist:todolist'))
        self.assertEqual(Todo.objects.count(), 0)
        self.assertEqual(TodoEditHistory.objects.count(), 0)
