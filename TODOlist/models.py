from django.db import models, transaction


class Todo(models.Model):
    Todo_theme = models.CharField(max_length=200)
    Todo_text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now=True)
    # Trueは未編集、Falseは一度以上内容が変わった編集済み。
    Edit_flag = models.BooleanField(
        default=True,
        help_text='Trueのときは未編集、Falseのときは編集済みです。',
    )

    def __str__(self):
        return self.Todo_theme

    @property
    def is_edited(self):
        return not self.Edit_flag

    def record_edit(self, previous_theme, previous_text):
        """内容が変わったときだけ編集済みにし、変更前後を履歴へ残す。"""
        if previous_theme == self.Todo_theme and previous_text == self.Todo_text:
            return None
        with transaction.atomic():
            self.Edit_flag = False
            self.save()
            return TodoEditHistory.objects.create(
                todo=self,
                previous_theme=previous_theme,
                previous_text=previous_text,
                new_theme=self.Todo_theme,
                new_text=self.Todo_text,
            )


class TodoEditHistory(models.Model):
    todo = models.ForeignKey(
        Todo,
        on_delete=models.CASCADE,
        related_name='edit_histories',
        verbose_name='TODO',
    )
    previous_theme = models.CharField('変更前のテーマ', max_length=200)
    previous_text = models.TextField('変更前の内容')
    new_theme = models.CharField('変更後のテーマ', max_length=200)
    new_text = models.TextField('変更後の内容')
    edited_at = models.DateTimeField('編集日時', auto_now_add=True)

    class Meta:
        ordering = ['-edited_at', '-pk']
        verbose_name = '編集履歴'
        verbose_name_plural = '編集履歴'

    def __str__(self):
        return f'{self.previous_theme} → {self.new_theme}'
