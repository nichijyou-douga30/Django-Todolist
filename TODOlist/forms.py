from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ('Todo_theme', 'Todo_text')
        labels = {
            'Todo_theme': 'テーマ',
            'Todo_text': 'やること(TODO)',
        }
        widgets = {
            'Todo_text': forms.Textarea(attrs={'rows': 5}),
        }
